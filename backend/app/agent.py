import os
import json
from openai import AsyncOpenAI
from .config import settings
from .session import get_session, update_session
from .booking import book_site_visit
from .escalation import request_human_callback
from .models import SessionData
from .llm import get_llm_client, get_llm_model

client = get_llm_client()

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "northstar_sales_agent.txt")

with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "update_lead_state",
            "description": "Whenever the customer explicitly provides one or more supported lead attributes, update all clearly stated attributes in the same turn before responding. Do not discard a lead attribute merely because another action, such as booking, is also requested in the same message. Only include fields that have been explicitly provided or clearly inferred.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "configuration": {"type": "string", "enum": ["2 BHK", "3 BHK"]},
                    "budget": {"type": "string"},
                    "purpose": {"type": "string"},
                    "current_location": {"type": "string"},
                    "purchase_timeline": {"type": "string"},
                    "interest_level": {"type": "string", "enum": ["low", "medium", "high"]},
                    "site_visit_requested": {"type": "boolean"},
                    "follow_up_required": {"type": "boolean"},
                    "contact_permission": {"type": "boolean"},
                    "language": {"type": "string"}
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_site_visit",
            "description": "Request a site visit booking for the customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "e.g., Saturday, Sunday"},
                    "time": {"type": "string", "description": "e.g., 11:00 AM, 2:00 PM"}
                },
                "required": ["date", "time"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_human_callback",
            "description": "Request a human sales representative to contact the customer.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "End the conversation when the user says goodbye or wants to stop.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    }
]

import re

def clean_final_response(text: str) -> str:
    if not text:
        return ""
    # Strip tool_call tags
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Strip <function=...> ... </function> 
    text = re.sub(r'<function=[^>]+>.*?(?:</function>)?', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Strip standalone parameter tags just in case
    text = re.sub(r'<parameter=[^>]+>.*?(?:</parameter>)?', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Strip internal reasoning phrases that leak
    bad_phrases = [
        r"I should inform the customer.*?\n",
        r"I need to tell the customer.*?\n",
        r"The system returned.*?\n",
        r"I will now.*?\n",
        r"Next I should.*?\n",
        r"According to the tool.*?\n",
        r"Tool result.*?\n",
        r"The booking was unsuccessful\.\.\..*?\n"
    ]
    for phrase in bad_phrases:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
    return text.strip()

async def process_chat(session_id: str, user_message: str) -> str:
    session = get_session(session_id)
    session.message_count += 1
    
    # Check for opt-out in the incoming message
    lower_msg = user_message.lower().strip().rstrip(".,?!")
    if lower_msg in ["please don't contact me again", "don't contact me", "stop messaging me", "don't contact me again"]:
        session.conversation_ended = True
        session.lead_state.contact_permission = False
        session.lead_state.conversation_outcome = "opted_out"
        update_session(session_id, session)
        return "Understood. I won't contact you again. Thank you for your time."
    
    # Append user message
    session.conversation_history.append({"role": "user", "content": user_message})
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + session.conversation_history
    
    # Call LLM
    response = await client.chat.completions.create(
        model=get_llm_model(),
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # Check if there are tool calls
    if response_message.tool_calls:
        # Append the assistant message with tool calls
        session.conversation_history.append(response_message.model_dump(exclude_none=True))
        
        # Sort tool calls so update_lead_state runs before book_site_visit
        sorted_tool_calls = sorted(
            response_message.tool_calls,
            key=lambda tc: 0 if tc.function.name == "update_lead_state" else 1
        )
        
        for tool_call in sorted_tool_calls:
            function_name = tool_call.function.name
            try:
                kwargs = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                kwargs = {}
                
            tool_response = {}
            
            if function_name == "update_lead_state":
                allowed_keys = {
                    "name", "phone", "email", "configuration", "budget", "purpose", "current_location", 
                    "purchase_timeline", "interest_level", "site_visit_requested", 
                    "follow_up_required", "contact_permission", "language"
                }
                
                is_valid = True
                error_message = ""
                error_code = ""
                validated_data = {}
                
                for k, v in kwargs.items():
                    if k not in allowed_keys:
                        is_valid = False
                        error_code = "unsupported_action"
                        error_message = f"Unsupported field '{k}' provided."
                        break
                    
                    if k == "configuration" and v:
                        norm = str(v).lower().replace("-", " ").strip()
                        if "2bhk" in norm.replace(" ", ""):
                            validated_data[k] = "2 BHK"
                        elif "3bhk" in norm.replace(" ", ""):
                            validated_data[k] = "3 BHK"
                        else:
                            is_valid = False
                            error_code = "invalid_configuration"
                            error_message = "Configuration must be one of: 2 BHK, 3 BHK."
                            break
                    elif k == "interest_level" and v:
                        if str(v).lower() not in ["low", "medium", "high"]:
                            is_valid = False
                            error_code = "invalid_tool_argument"
                            error_message = "Interest level must be low, medium, or high."
                            break
                        validated_data[k] = str(v).lower()
                    else:
                        validated_data[k] = v
                
                if is_valid:
                    for k, v in validated_data.items():
                        if hasattr(session.lead_state, k) and v is not None:
                            setattr(session.lead_state, k, v)
                    tool_response = {"success": True, "message": "Lead state updated successfully."}
                else:
                    tool_response = {"success": False, "error": error_code, "message": error_message}
                
            elif function_name == "book_site_visit":
                date = kwargs.get("date")
                time = kwargs.get("time")
                
                missing_fields = []
                if not session.lead_state.name:
                    missing_fields.append("name")
                if not session.lead_state.phone:
                    missing_fields.append("phone")
                if not session.lead_state.email:
                    missing_fields.append("email")
                
                if not date or not time:
                    tool_response = {
                        "success": False, 
                        "error": "missing_required_field", 
                        "message": "Both date and time are required to book a site visit."
                    }
                elif missing_fields:
                    missing_str = ", ".join(missing_fields)
                    tool_response = {
                        "success": False,
                        "error": "missing_contact_details",
                        "message": f"Cannot book site visit. Missing required contact details: {missing_str}. Ask the customer for these details before booking."
                    }
                else:
                    result = book_site_visit(str(date), str(time))
                    session.lead_state.site_visit_requested = True
                    if result.get("success"):
                        session.lead_state.site_visit_status = "booked"
                        session.lead_state.site_visit_date = result.get("date")
                        session.lead_state.site_visit_time = result.get("time")
                        session.lead_state.booking_reference = result.get("booking_id")
                        session.lead_state.conversation_outcome = "site_visit_booked"
                    else:
                        session.lead_state.site_visit_status = "failed"
                    tool_response = result
                
            elif function_name == "request_human_callback":
                result = request_human_callback()
                session.lead_state.human_escalation = True
                if result.get("success"):
                    session.lead_state.conversation_outcome = "human_escalation_requested"
                    session.conversation_ended = True # End conversation on successful handoff
                tool_response = result
                
            elif function_name == "end_conversation":
                session.conversation_ended = True
                if "contact_permission" in kwargs:
                    session.lead_state.contact_permission = kwargs.get("contact_permission")
                if session.lead_state.contact_permission is False:
                    session.lead_state.conversation_outcome = "opted_out"
                tool_response = {"success": True, "message": "Conversation ended."}
                
            else:
                tool_response = {"error": f"Unknown function: {function_name}"}
                
            # Append tool result
            session.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(tool_response)
            })
            
        # Get final response from LLM after tool executions
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + session.conversation_history
        final_response = await client.chat.completions.create(
            model=get_llm_model(),
            messages=messages,
            tools=TOOLS, # Keep tools in case it needs to do something else, though usually we don't force it
            tool_choice="none" # Ensure it just answers text now
        )
        final_text = clean_final_response(final_response.choices[0].message.content or "")
        session.conversation_history.append({"role": "assistant", "content": final_text})
        update_session(session_id, session)
        return final_text
    
    else:
        # No tool calls, just text
        reply = clean_final_response(response_message.content or "")
        session.conversation_history.append({"role": "assistant", "content": reply})
        update_session(session_id, session)
        return reply
