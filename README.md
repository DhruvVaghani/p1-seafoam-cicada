# Phase 1 — Public

Minimal mock API and multi-turn demo interactions for ticket triage.

# Ticket Triage Agent (LangGraph)

This project implements a minimal AI agent using LangGraph that:
- Ingests a customer support ticket
- Classifies the issue type using an LLM
- Fetches order details via a ToolNode
- Drafts a customer-facing reply

The agent is exposed via a FastAPI endpoint and includes LangSmith tracing for observability.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Git

### Clone the repository
```bash
git clone <your-repo-url>
cd p1-seafoam-cicada
