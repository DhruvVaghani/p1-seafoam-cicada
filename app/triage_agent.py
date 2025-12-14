from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator
import os
import json
import re
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"


# Shared state object that carries ticket information and agent outputs across all LangGraph nodes.
class TriageState(TypedDict):
    """
    Represents the state of the ticket triage process.
    """
    messages: Annotated[List[Dict[str, Any]], operator.add]
    ticket_text: str 
    order_id: Optional[str] 
    issue_type: Optional[str] 
    evidence: Optional[Dict[str, Any]] 
    recommendation: Optional[str]

# Entry node that reads the incoming ticket and extracts the order ID if present.
def ingest(state: TriageState) -> TriageState:
    """Sets the initial ticket_text and attempts to extract an order_id."""
    
    # The input will come in via the state, but we need to ensure the ticket_text is present.
 
    text = state["ticket_text"]
    order_id = state.get("order_id")

    """If order_id is missing, attempt to extract it from the text (as done in /triage/invoke)"""
    if not order_id:
        # Regex is: " (ORD\d{4})" [cite: 67]
        import re
        m = re.search(r"(ORD\d{4})", text, re.IGNORECASE)
        if m:
            order_id = m.group(1).upper()
            
    print(f"--- Ingest: Ticket text loaded. Order ID: {order_id} ---")

    # Update the state
    return {
        "ticket_text": text, 
        "order_id": order_id,
        "order_id": order_id,
        "issue_type": state.get("issue_type"),  # Preserve existing
        "evidence": state.get("evidence"),
        "recommendation": state.get("recommendation")
    }

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


from pydantic import BaseModel

class IssueClassification(BaseModel):
    issue_type: str
    evidence: str

# Uses an LLM to classify the customer’s issue into a predefined support category
def classify_issue(state: TriageState) -> dict:
    """
    Uses an LLM to classify the issue type from the ticket text.
    """
    text = state["ticket_text"]

    prompt = f"""
You are a support ticket classifier.

Classify the issue type using ONE of:
- refund_request
- late_delivery
- missing_item
- damaged_item
- wrong_item
- unknown

Ticket:
{text}

Respond with ONLY a JSON object (no markdown, no explanation):
{{"issue_type": "category_here", "reasoning": "brief explanation"}}
"""

    response = llm.with_structured_output(IssueClassification).invoke(prompt)
   

    return {
        "messages": [AIMessage(content=response.json())],
        "issue_type": response.issue_type,
        "evidence": response.evidence,
    }


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MOCK_DIR = os.path.join(ROOT, "mock_data")

def load_orders():
    with open(os.path.join(MOCK_DIR, "orders.json"), "r") as f:
        return json.load(f)

ORDERS = load_orders()

# Tool function that retrieves order details from mock data using the extracted order ID.
def fetch_order_tool(order_id: str) -> dict:
    """
    Fetch order details for a given order_id from mock order data.
    """
    for o in ORDERS:
        if o["order_id"] == order_id:
            return o
    raise ValueError("Order not found")


# LangGraph ToolNode that executes the order lookup tool as part of the workflow.
fetch_order_node = ToolNode(
    tools=[fetch_order_tool]
)


# Generates a professional, customer-facing response based on the issue type and order context.
def draft_reply(state: TriageState) -> dict:
    prompt = f"""
You are a customer support assistant.

Issue type: {state.get("issue_type")}
Order ID: {state.get("order_id")}

Write a professional, helpful reply to the customer.
# Guidelines:
# - Be concise and answer in only about 1 to 2 lines.
"""

    response = llm.invoke(prompt)

    return {
        "messages": [AIMessage(content=response.content)],
        "recommendation": response.content
    }


from langgraph.graph import StateGraph, END

def route_after_ingest(state: TriageState) -> str:
    """
    If order_id was successfully extracted, proceed.
    Otherwise, stop execution (error case).
    """
    if state.get("order_id"):
        return "classify_issue"
    else:
        return END
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

def build_triage_graph():
    graph = StateGraph(TriageState)

    # Register nodes
    graph.add_node("ingest", ingest)
    graph.add_node("classify_issue", classify_issue)
    graph.add_node("fetch_order", fetch_order_node)
    graph.add_node("draft_reply", draft_reply)

    # Entry point
    graph.set_entry_point("ingest")

    # Conditional control flow after ingest
    graph.add_conditional_edges(
        "ingest",
        route_after_ingest,
        {
            "classify_issue": "classify_issue",
            END: END
        }
    )

    # Linear flow
    graph.add_edge("classify_issue", "fetch_order")
    graph.add_edge("fetch_order", "draft_reply")
    graph.add_edge("draft_reply", END)

    return graph.compile(checkpointer=memory)
