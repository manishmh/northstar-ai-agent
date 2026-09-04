# Northstar Homes AI Sales Agent — Backend

This is the backend implementation for the Northstar Homes AI Sales Agent assignment.

## Project Overview

This API powers a conversational AI sales agent designed for Northstar Homes. It acts as a friendly and capable sales representative for the "Northstar One" project in Gurugram. 

### Design Philosophy

The core architectural principle of this system is:
> **The LLM can request an action, but the backend decides whether that action is valid and what actually happened.**

The LLM is not treated as an authoritative business-logic layer.

LLM:
- understands intent
- extracts customer information
- requests supported actions
- generates conversational responses

Backend:
- validates tool arguments
- enforces business rules
- owns session state
- owns booking results
- generates booking/escalation references
- prevents invalid LLM output from corrupting state

This means that the agent parses context naturally but calls defined backend "tools" to confirm bookings, escalate to human reps, or log important lead states. The LLM never hallucinates booking IDs or invents state that hasn't been confirmed by the backend.

## Architecture

- **Framework**: FastAPI (Python)
- **Memory/State**: Simple in-memory session manager.
- **LLM Integration**: OpenRouter via OpenAI Python SDK (utilizing standard tool-calling).
- **Testing**: `pytest` and `fastapi.testclient`, mocking external LLM calls to keep tests reliable.

### Request Flow
```
Customer -> POST /chat 
   -> Validation (Max length check)
   -> Session loaded
   -> OpenRouter LLM Call (with Tools: update_lead_state, book_site_visit, etc.)
   -> Backend executes required tools deterministically
   -> Agent responds naturally
   -> Session updated
```

## Setup & Running

1. **Install dependencies**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in:
   ```env
   OPENROUTER_API_KEY=your_key
   LLM_MODEL=openrouter/free
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   MAX_MESSAGE_LENGTH=4000
   ```
   *(To use OpenAI directly, update the BASE_URL to OpenAI's and supply OPENAI_API_KEY)*

3. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Examples

**Health Check**
```bash
curl -X GET http://localhost:8000/health
```

**Chat**
```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{"session_id": "user123", "message": "Hi, I am looking for a 3 BHK in Gurugram."}'
```

**Analytics**
```bash
curl -X GET http://localhost:8000/analytics/user123
```

**Reset Session**
```bash
curl -X POST http://localhost:8000/reset \
-H "Content-Type: application/json" \
-d '{"session_id": "user123"}'
```

## Security Approach
- **Prompt Isolation**: System instructions heavily restrict agent scope to real-estate only.
- **Input Validation**: Hard bounds on payload size limit injection complexity.
- **No Direct Executions**: LLM can only pick from a curated list of strict tool calls which map to safe Python functions.
- **Data Protection**: Secrets are loaded through Pydantic settings from the environment, never committed.

## Known Limitations & Assumptions
- **In-Memory Store**: `Dict`-based session storage resets on server restart. For production, Redis or Postgres is required.
- **Booking Simulator**: Only 4 specific slots are accepted as "valid" slots. 
- **Tool-calling limits**: Using models with poor tool calling might cause unstable behavior. A robust model (e.g. Gemini 3.1 Pro or GPT-4o) is highly recommended.

## AI Tools Used
- Written and refined alongside an AI Assistant for boilerplate scaffolding, architecture sanity checks, and test-suite generation.
