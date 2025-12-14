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
git clone https://github.com/DhruvVaghani/p1-seafoam-cicada.git
cd p1-seafoam-cicada

### Create and activate virtual environment

#### Windows (PowerShell):
python -m venv Assess_env
.\Assess_env\Scripts\Activate

#### macOS / Linux:
python3 -m venv Assess_env
source Assess_env/bin/activate

#### Install dependencies:
pip install -r requirements.txt


#### Environment variables
Please create your own Open_AI_KEY and LANGCHAIN_API_KEY

Create a .env file in the project root with the following:
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
LANGCHAIN_API_KEY="ls-xxxxxxxxxxxxxxxx"
LANGCHAIN_PROJECT = "triage-agent"
LANGCHAIN_TRACING_V2 = "true"

Note: .env is ignored by git and is not  committed.
