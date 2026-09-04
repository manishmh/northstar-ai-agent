# Northstar Homes AI Sales Agent — Project Context & Build Specification

## 1. Project Purpose

Build the backend for a simple AI conversational sales agent for a fictional real-estate company, **Northstar Homes**, as part of a Forward Deployed Engineer assignment.

The assignment explicitly prioritizes:

1. Prompt engineering
2. Agent behavior
3. Conversation context/memory
4. Correct handling of customer intents and objections
5. Site-visit booking simulation
6. Correct handling of booking failure
7. Lead analytics after the conversation
8. Clear, simple implementation

Do **not** over-engineer the project. The UI will be built later. The current phase is backend + tests.

The backend must use **FastAPI / Python**. Express.js or another backend framework is not acceptable.

## 2. Product Scenario

- Company: Northstar Homes
- Project: Northstar One
- Location: Sector 79, Gurugram
- Configurations: 2 BHK, 3 BHK
- 2 BHK: ₹1.35 crore onwards
- 3 BHK: ₹1.75 crore onwards
- Languages: English, Hindi, Hinglish

The agent should understand requirements, answer relevant questions, qualify leads, handle objections, arrange site visits, handle failures honestly, offer human escalation, respect opt-out/busy customers, end naturally, and produce structured analytics.

## 3. Current Scope

### In scope
- FastAPI application
- OpenRouter LLM integration
- System prompt
- Conversation/session memory
- Structured lead state
- Agent response generation
- Site-visit booking simulator
- Human escalation simulator
- Conversation-ending detection
- Analytics generation
- Security/abuse handling
- Automated tests
- README and `.env.example`

### Not currently in scope
- React UI
- Authentication system
- Real CRM
- Real calendar
- WhatsApp
- Twilio
- Voice infrastructure
- Redis
- PostgreSQL
- Vector database/RAG
- Admin dashboard
- Production deployment

Keep infrastructure intentionally simple.

## 4. Architecture

```text
Customer -> FastAPI /chat -> Session State + System Prompt -> OpenRouter LLM
                                      |
                                      +-> validated backend actions
                                      |     +-> booking simulator
                                      |     +-> human escalation simulator
                                      |
                                      +-> lead state / analytics
                                      v
                                   Response
```

The LLM controls conversational behavior. The backend controls deterministic actions and state changes. Never allow the model to simply claim a booking or escalation succeeded.

## 5. LLM Provider

Use **OpenRouter** because an OpenAI API key is not available. Keep the model configurable:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

Do not hardcode credentials. Use an OpenAI-compatible chat-completions interface where practical. Do not make the architecture dependent on provider-specific features unless necessary.

## 6. System Prompt Responsibilities

The prompt is one of the most important parts of the assignment.

It must enforce:

- Natural human sales-representative behavior
- Concise responses suitable for chat and voice
- One useful question at a time
- No repeated questions when information is known
- English/Hindi/Hinglish language matching
- Grounding strictly in the provided Northstar facts
- No invented price, discount, availability, inventory, amenities, tower count, floor, area, possession, construction, payment plans, financing, approvals, specifications, landmarks, or other unsupported information
- Honest handling of unknown questions
- Natural qualification: name, configuration, budget, purpose, location, timeline, interest, site-visit interest
- No forced questionnaire behavior
- Objection handling: expensive, discount, browsing, busy, contact later, do not contact, human request
- Correct site-visit behavior
- Correct handling of booking failure
- Human escalation
- Natural conversation ending
- Prompt-injection/jailbreak resistance
- Refusal/redirect of unrelated tasks

## 7. Security and Abuse Handling

Treat customer input as untrusted.

The agent must resist:

- Prompt injection
- Jailbreaks
- System-prompt extraction
- Requests to reveal internal instructions
- Requests for credentials/backend information
- Requests to change its role
- Requests to ignore previous instructions
- Unrelated tasks such as coding or general problem solving
- Attempts to manipulate booking/tool actions
- Excessively long, repetitive, malformed, or abusive input

The model should briefly redirect unrelated requests back to Northstar Homes.

The system prompt is not a real security boundary. Backend controls must enforce input limits, rate limits where implemented, action allowlists, booking validation, output handling, and secret management. Never put secrets in the prompt.

## 8. Conversation Memory

Use simple session-based memory for the assignment. Each session retains recent conversation history and structured lead state.

Lead state:

```text
name
configuration
budget
purpose
current_location
purchase_timeline
interest_level
site_visit_requested
site_visit_status
site_visit_date
site_visit_time
booking_reference
follow_up_required
follow_up_time
human_escalation
contact_permission
conversation_outcome
language
```

Unknown fields remain null/unknown. Never infer a customer fact without sufficient evidence.

The agent must remember provided information, avoid repeated questions, update corrected information, prefer the latest explicit customer statement, and distinguish facts from assumptions.

## 9. Qualification

Qualification is contextual, not a checklist.

Capture when supported:
- Configuration: 2 BHK / 3 BHK / undecided
- Budget: approximate stated budget
- Purpose: self-use / investment / family / other stated purpose
- Timeline: browsing / later / active / soon, only when supported
- Interest: low / medium / high / unknown

Do not tell the customer they are "qualified" simply because their budget exceeds a starting price.

## 10. Booking Simulator

Implement a deterministic mock booking service. Example slots:

```text
Saturday 11:00 AM
Saturday 2:00 PM
Sunday 11:00 AM
Sunday 4:00 PM
```

Success should return structured data such as:

```json
{"success": true, "date": "Saturday", "time": "11:00 AM", "booking_id": "NS-12345"}
```

Failure should return something like:

```json
{"success": false, "reason": "slot_unavailable", "alternatives": ["Saturday 2:00 PM", "Sunday 11:00 AM"]}
```

Booking IDs are backend-generated. The LLM must never invent them.

## 11. Human Escalation

Implement a simple mock action such as `request_human_callback()` returning success/reference information. The model should only claim escalation succeeded when the backend action succeeds.

## 12. Agent Actions

Keep the action system simple. Supported actions may include:

```text
book_site_visit
request_human_callback
end_conversation
```

The backend validates actions. Never allow arbitrary function execution.

If the chosen OpenRouter model does not reliably support tool calling, use a constrained structured response and validate it strictly in Python.

Do not introduce a complex agent framework.

## 13. Analytics

When a conversation ends, produce structured analytics containing:

- Budget
- Configuration
- Purpose
- Current location
- Purchase timeline
- Interest level
- Site visit requested
- Site visit status
- Follow-up required
- Human escalation
- Contact permission
- Conversation outcome
- Language
- Message count

Missing information must be null/unknown, never invented.

Example:

```json
{
  "lead_summary": {
    "name": "Rahul",
    "configuration": "3 BHK",
    "budget": "₹2 crore",
    "purpose": "self-use",
    "current_location": "Delhi",
    "purchase_timeline": "within 3 months",
    "interest_level": "high",
    "site_visit_requested": true,
    "site_visit_status": "booked",
    "follow_up_required": false,
    "human_escalation": false,
    "contact_permission": true
  },
  "conversation": {
    "language": "Hinglish",
    "message_count": 10,
    "conversation_outcome": "site_visit_booked"
  }
}
```

## 14. API Design

Keep the API small.

### GET /health
Service health.

### POST /chat

Request:

```json
{"session_id": "abc123", "message": "I'm looking for a 3 BHK around 2 crore"}
```

Response should include at least:

```json
{"session_id": "abc123", "reply": "...", "conversation_ended": false}
```

### POST /reset
Reset a session.

### GET /analytics/{session_id}
Return current/final analytics.

Do not add unnecessary endpoints.

## 15. Error Handling

Handle missing API key, OpenRouter failures/timeouts, invalid model responses, invalid actions, booking failures, unknown sessions, excessive input, and malformed requests.

Do not leak API keys, stack traces, internal prompts, or backend details.

## 16. Testing Requirements

Create scenario-based tests covering behavior rather than only HTTP 200 responses.

Required scenarios:

1. Basic enquiry
2. Pricing
3. Hinglish
4. Qualification and memory
5. Price objection
6. Unknown project information
7. Prompt injection
8. Unrelated request such as code generation
9. Excessively long input rejected before LLM processing
10. Site-visit success
11. Site-visit failure with alternatives
12. Human escalation
13. Opt-out
14. Busy/contact-later request
15. Context retention and correction

Avoid brittle exact-string assertions for LLM responses. Assert important facts, state transitions, and behavior.

## 17. Suggested Structure

```text
northstar-ai-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── session.py
│   │   ├── agent.py
│   │   ├── booking.py
│   │   ├── escalation.py
│   │   ├── analytics.py
│   │   └── prompts/
│   │       └── northstar_sales_agent.txt
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_booking.py
│   │   ├── test_security.py
│   │   └── scenarios.md
│   ├── requirements.txt
│   └── .env.example
├── README.md
├── PROJECT_CONTEXT.md
├── .gitignore
└── LICENSE
```

This is a recommendation. Simplify it if a file does not provide meaningful separation.

## 18. Implementation Principles

Prefer FastAPI, Pydantic, Python standard library, simple session storage, clear service functions, small modules, deterministic backend actions, and scenario tests.

Avoid LangChain/LangGraph, microservices, Redis, Celery, Kubernetes, RAG/vector databases, complex authentication, and unnecessary abstraction unless a real requirement appears.

## 19. Responsibility Split

### Prompt
- Conversation style
- Language
- Qualification behavior
- Objections
- Unknown questions
- Scope
- Prompt-injection resistance
- Ending
- Escalation intent

### Backend
- Input limits
- Rate limiting if implemented
- Session state
- Booking availability
- Booking IDs
- Booking success/failure
- Human escalation action
- Secret management
- Action validation
- Analytics
- API errors

The model is not the source of truth for state-changing actions.

## 20. Voice Compatibility

The eventual product may support voice. Keep responses concise, spoken-language friendly, avoid markdown-heavy responses, avoid huge lists, confirm important dates/times, and ask one main question at a time. Do not build voice infrastructure yet.

## 21. README Requirements

README must explain:

- Project overview
- Architecture
- Setup and environment variables
- How to run FastAPI
- API examples
- Prompt approach
- Memory approach
- Booking approach
- Security approach
- Testing
- Assumptions
- Known limitations
- AI tools used

## 22. Later Demo Requirements

Eventually demonstrate:

### A — Qualified lead
Project enquiry -> qualification -> site visit -> analytics.

### B — Hinglish + objection
Hinglish conversation -> price objection -> natural handling.

### C — Security + booking failure
Prompt injection/unrelated request -> safe redirect -> unavailable site-visit slot -> honest failure -> alternatives/human escalation.

## 23. Evaluation Priorities

Prioritize:

1. Prompt quality
2. Agent behavior
3. Context/memory
4. Booking correctness
5. Failure handling
6. Analytics
7. Security
8. Code clarity
9. Tests
10. UI later

A simple UI with excellent agent behavior is better than a beautiful UI with weak logic.

## 24. Backend Definition of Done

The backend is complete when:

- FastAPI runs
- OpenRouter model is configurable through `.env`
- System prompt is implemented
- Sessions retain context
- Lead state updates correctly
- English/Hindi/Hinglish behavior works
- Pricing remains grounded
- Unknown questions are safe
- Prompt injection attempts are resisted
- Unrelated requests are redirected
- Opt-out is respected
- Human escalation mock works
- Site-visit success works
- Site-visit failure works
- Booking IDs are backend-generated
- Analytics are generated
- Input limits are enforced
- Errors do not leak secrets/internal details
- Scenario tests exist
- README explains architecture and decisions
- No unnecessary infrastructure has been introduced

## 25. Important Development Rule

Do not start building the frontend.

First make the backend behavior reliable and testable.

Do not add a feature merely because it is technically interesting. Every implementation decision should support an assignment evaluation criterion.
