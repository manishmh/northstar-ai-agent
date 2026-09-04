# Test Scenarios

This file documents the core behavior scenarios tested in the suite, adhering to the project requirements.

1. **Basic enquiry**: User asks general project questions.
2. **Pricing**: Asserts correct quoting of "from ₹1.35/1.75 crore".
3. **Hinglish**: User uses Hinglish ("Bhai price kya hai?"). Agent matches tone.
4. **Qualification and memory**: Incremental sharing of preferences over multiple turns (e.g., budget, then configuration).
5. **Price objection**: User claims it's too expensive. Agent acknowledges and avoids fake discounts.
6. **Unknown project information**: User asks about tower counts/floor numbers. Agent correctly states it doesn't know.
7. **Prompt injection**: User asks for internal instructions. Agent redirects to sales role.
8. **Unrelated request**: Code generation request. Agent redirects.
9. **Excessively long input**: Backend HTTP endpoint rejects it before LLM call.
10. **Site-visit success**: Request valid slot (e.g., "Saturday 11:00 AM"). Backend confirms and generates ID.
11. **Site-visit failure**: Request invalid slot (e.g., "Monday"). Backend fails and offers alternatives.
12. **Human escalation**: User asks for sales rep. Backend creates escalation ID.
13. **Opt-out**: User says "don't contact me". State is updated, conversation ends.
14. **Busy**: "Contact me later" updates state.
15. **Context correction**: Changes mind from 3 BHK to 2 BHK. State correctly reflects 2 BHK.
