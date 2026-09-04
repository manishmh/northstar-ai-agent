# Northstar Homes AI Sales Agent

A conversational AI sales agent built for the Northstar Homes assignment.

The agent helps customers understand **Northstar One**, qualify their requirements, and arrange a simulated site visit. It supports **English, Hindi, and Hinglish** and is designed for both chat and voice-style conversations.

## System Prompt

The complete system prompt used by the sales agent is available here:

**[View the Northstar Sales Agent System Prompt](backend/app/prompts/northstar_sales_agent.txt)**

The prompt defines the agent's conversation behavior, qualification flow, language handling, objection handling, booking flow, escalation rules, and boundaries around unsupported information.

## How to Run

### Prerequisites

- Python 3.10+
- Node.js 18+
- API key for either OpenAI or OpenRouter

### 1. Start the Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Add your API key to `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=your_model_here

# Or use OpenRouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=your_model_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

If `OPENAI_API_KEY` is configured, the agent uses OpenAI. Otherwise, it uses OpenRouter.

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

### 2. Start the Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## Key Assumptions

This assignment uses a simulated environment rather than real CRM or calendar integrations.

* The agent only has confirmed information provided in the assignment:

  * **Northstar Homes**
  * **Northstar One**
  * **Sector 79, Gurugram**
  * **2 BHK — ₹1.35 crore onwards**
  * **3 BHK — ₹1.75 crore onwards**
* The agent does not invent amenities, discounts, availability, floor plans, possession dates, financing details, or other unsupported information.
* Site-visit booking is simulated by the backend.
* Human escalation is simulated.
* Conversation sessions are stored in memory. In production, this layer could be replaced with Redis or PostgreSQL.
* Lead information is maintained as conversation state.
* LLM tool calls request backend actions, but the backend validates those actions before executing them.

## Known Limitations

* **No persistent database is used for this assignment.** The focus is on demonstrating the AI agent, conversation memory, qualification, and backend actions rather than introducing database infrastructure that is not required by the assignment. An in-memory session store keeps the prototype simple and easy to run locally, while the session layer can be replaced with Redis or PostgreSQL in production. Active conversations are therefore cleared when the backend restarts.
* Site-visit availability is simulated and is not connected to a real calendar.
* Human escalation does not connect to an actual sales representative or CRM.
* No real email, SMS, WhatsApp, or calling integration.
* The agent's knowledge is limited to the project information supplied in the assignment.
* Voice-compatible conversation behavior is implemented, but real telephony/STT/TTS integration is outside the assignment scope.

## AI Tools Used

AI-assisted development was used during implementation and testing.

* **Claude Code / Claude** — code generation, debugging, refactoring, test cases, and prompt iteration.
* **OpenAI / OpenRouter models** — runtime LLM for the sales agent.

AI-generated code and suggestions were manually reviewed, tested, and modified as required.

## Architecture

```text
Customer
   │
   ▼
React + Vite Chat UI
   │
   ▼
FastAPI Backend
   │
   ├── Session / Lead Memory
   ├── System Prompt
   ├── LLM Provider
   │     ├── OpenAI
   │     └── OpenRouter
   │
   └── Backend Actions
         ├── Lead State Updates
         ├── Site Visit Booking
         └── Human Escalation
```

---

For the detailed architecture, conversation flows, prompt design, validation, and testing approach, please refer to the accompanying demo video.
