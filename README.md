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
```
### Create and activate virtual environment
```bash
#### Windows (PowerShell):####
python -m venv Assess_env
.\Assess_env\Scripts\Activate

#### macOS / Linux:#####
python3 -m venv Assess_env
source Assess_env/bin/activate
```
### Install dependencies:
```bash
pip install -r requirements.txt

```
### Environment variables
Please create your own Open_AI_KEY and LANGCHAIN_API_KEY

Create a .env file in the project root with the following:
```bash
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
LANGCHAIN_API_KEY="ls-xxxxxxxxxxxxxxxx"
LANGCHAIN_PROJECT = "triage-agent"
LANGCHAIN_TRACING_V2 = "true"
```
Note: .env is ignored by git and is not  committed.

#### Start the app from the repo root folder using this command
```bash
uvicorn app.main:app --reload


```
### Open a NEW terminal window/tab 
### Leave uvicorn running in Terminal 1.
### Open Terminal 2 

In the terminal 2 Run the curl command in the command prompt (cmd)
```bash
curl -X POST http://127.0.0.1:8000/triage/invoke -H "Content-Type: application/json" -d "{ \"conversation_id\": \"P1-DEMO-004\", \"ticket_text\": \"Wrong item shipped for order ORD1006.\" }"

```

### Langsmith tracings
<img width="1257" height="895" alt="image" src="https://github.com/user-attachments/assets/74cd7e10-5fa1-4fd6-842d-a4e277d894b7" />

