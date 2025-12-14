
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json, os, re
from triage_agent import build_triage_graph

app = FastAPI(title="Phase 1 Mock API")
graph = build_triage_graph()



ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MOCK_DIR = os.path.join(ROOT, "mock_data")

def load(name):
    with open(os.path.join(MOCK_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)

ORDERS = load("orders.json")
ISSUES = load("issues.json")
REPLIES = load("replies.json")

class TriageInput(BaseModel):
    ticket_text: str
    order_id: str | None = None

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/orders/get")
def orders_get(order_id: str = Query(...)):
    for o in ORDERS:
        if o["order_id"] == order_id: return o
    raise HTTPException(status_code=404, detail="Order not found")

@app.get("/orders/search")
def orders_search(customer_email: str | None = None, q: str | None = None):
    matches = []
    for o in ORDERS:
        if customer_email and o["email"].lower() == customer_email.lower():
            matches.append(o)
        elif q and (o["order_id"].lower() in q.lower() or o["customer_name"].lower() in q.lower()):
            matches.append(o)
    return {"results": matches}

@app.post("/classify/issue")
def classify_issue(payload: dict):
    text = payload.get("ticket_text", "").lower()
    for rule in ISSUES:
        if rule["keyword"] in text:
            return {"issue_type": rule["issue_type"], "confidence": 0.85}
    return {"issue_type": "unknown", "confidence": 0.1}

def render_reply(issue_type: str, order):
    template = next((r["template"] for r in REPLIES if r["issue_type"] == issue_type), None)
    if not template: template = "Hi {{customer_name}}, we are reviewing order {{order_id}}."
    return template.replace("{{customer_name}}", order.get("customer_name","Customer")).replace("{{order_id}}", order.get("order_id",""))

@app.post("/reply/draft")
def reply_draft(payload: dict):
    return {"reply_text": render_reply(payload.get("issue_type"), payload.get("order", {}))}

@app.post("/triage/invoke")
def triage_invoke(payload: dict):
    conversation_id = payload.get("conversation_id", "default")

    result = graph.invoke(
        {
            "ticket_text": payload["ticket_text"],
            "messages": []
        },
        config={
            "configurable": {
                "thread_id": conversation_id
            }
        }
    )

    return {
        "order_id": result.get("order_id"),
        "issue_type": result.get("issue_type"),
        "recommendation": result.get("recommendation")
    }

