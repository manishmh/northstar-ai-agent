import pytest
import json
from unittest.mock import patch, AsyncMock
from app.agent import process_chat
from app.session import get_session, reset_session
from app.models import SessionData

@pytest.fixture(autouse=True)
def setup_and_teardown():
    reset_session("test_agent_session")
    yield
    reset_session("test_agent_session")

# Helpers to mock the OpenAI response
class MockToolFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockToolCall:
    def __init__(self, id, function):
        self.id = id
        self.type = "function"
        self.function = function

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls
        self.role = "assistant"
    
    def model_dump(self, exclude_none=False):
        d = {"role": self.role, "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in self.tool_calls]
        return d

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

def build_mock_responses(tool_calls=None, final_text="Done."):
    msg1 = MockMessage(content=None, tool_calls=tool_calls)
    msg2 = MockMessage(content=final_text)
    return [MockResponse([MockChoice(msg1)]), MockResponse([MockChoice(msg2)])]


@pytest.mark.asyncio
async def test_lead_state_valid_updates():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc1 = MockToolCall("call_1", MockToolFunction("update_lead_state", json.dumps({"configuration": "2 BHK"})))
        mock_create.side_effect = build_mock_responses([tc1])
        await process_chat("test_agent_session", "I want a 2 BHK")
        session = get_session("test_agent_session")
        assert session.lead_state.configuration == "2 BHK"
        
        tc2 = MockToolCall("call_2", MockToolFunction("update_lead_state", json.dumps({"configuration": "3 BHK"})))
        mock_create.side_effect = build_mock_responses([tc2])
        await process_chat("test_agent_session", "I want a 3 BHK instead")
        assert session.lead_state.configuration == "3 BHK"


@pytest.mark.asyncio
async def test_lead_state_invalid_updates_rejected():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("update_lead_state", json.dumps({"configuration": "4 BHK"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "I want a 4 BHK")
        session = get_session("test_agent_session")
        assert session.lead_state.configuration is None
        
        # Tool call response should be a validation failure
        tool_response_content = session.conversation_history[-2]["content"]
        assert "invalid_configuration" in tool_response_content


@pytest.mark.asyncio
async def test_lead_state_normalization():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("update_lead_state", json.dumps({"configuration": "2bhk"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "2bhk")
        session = get_session("test_agent_session")
        assert session.lead_state.configuration == "2 BHK"


@pytest.mark.asyncio
async def test_lead_state_partial_invalid_update_fails_completely():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("update_lead_state", json.dumps({"budget": "1 cr", "configuration": "villa"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "I have 1 cr for a villa")
        session = get_session("test_agent_session")
        # Neither should be updated
        assert session.lead_state.budget is None
        assert session.lead_state.configuration is None


@pytest.mark.asyncio
async def test_booking_valid_slot():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("book_site_visit", json.dumps({"date": "Saturday", "time": "11:00 AM"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "Book for Saturday 11am")
        session = get_session("test_agent_session")
        assert session.lead_state.site_visit_status == "booked"
        assert session.lead_state.booking_reference is not None
        assert session.lead_state.booking_reference.startswith("NS-")


@pytest.mark.asyncio
async def test_booking_invalid_slot():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("book_site_visit", json.dumps({"date": "Monday", "time": "11:00 AM"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "Book for Monday 11am")
        session = get_session("test_agent_session")
        assert session.lead_state.site_visit_status == "failed"
        tool_response = json.loads(session.conversation_history[-2]["content"])
        assert "alternatives" in tool_response


@pytest.mark.asyncio
async def test_booking_missing_fields():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("book_site_visit", json.dumps({"date": "Saturday"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "Book for Saturday")
        session = get_session("test_agent_session")
        tool_response = json.loads(session.conversation_history[-2]["content"])
        assert tool_response["success"] is False
        assert tool_response["error"] == "missing_required_field"


@pytest.mark.asyncio
async def test_human_escalation():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("request_human_callback", json.dumps({})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "Call me")
        session = get_session("test_agent_session")
        assert session.lead_state.human_escalation is True
        tool_response = json.loads(session.conversation_history[-2]["content"])
        assert "reference_id" in tool_response
        assert tool_response["reference_id"].startswith("HC-")


@pytest.mark.asyncio
async def test_unsupported_fields_rejected():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("update_lead_state", json.dumps({"discount": "20%"})))
        mock_create.side_effect = build_mock_responses([tc])
        await process_chat("test_agent_session", "discount please")
        session = get_session("test_agent_session")
        tool_response = json.loads(session.conversation_history[-2]["content"])
        assert tool_response["success"] is False
        assert tool_response["error"] == "unsupported_action"


@pytest.mark.asyncio
async def test_scenario_d_unavailable_slot():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("book_site_visit", json.dumps({"date": "Tuesday", "time": "2:00 PM"})))
        msg1 = MockMessage(content=None, tool_calls=[tc])
        msg2 = MockMessage(content="That slot is unavailable. We have Saturday 11:00 AM instead.")
        mock_create.side_effect = [MockResponse([MockChoice(msg1)]), MockResponse([MockChoice(msg2)])]
        
        reply = await process_chat("test_agent_session", "Tuesday 2 PM please")
        assert "unavailable" in reply
        
        session = get_session("test_agent_session")
        assert session.lead_state.site_visit_status == "failed"
        tool_resp = json.loads(session.conversation_history[-2]["content"])
        assert tool_resp["success"] is False
        assert tool_resp["alternatives"]


@pytest.mark.asyncio
async def test_opt_out():
    reply = await process_chat("test_agent_session", "Don't contact me.")
    assert "won't contact you again" in reply
    
    session = get_session("test_agent_session")
    assert session.conversation_ended is True
    assert session.lead_state.contact_permission is False
    assert session.lead_state.conversation_outcome == "opted_out"


@pytest.mark.asyncio
async def test_no_tool_call_leak():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        msg = MockMessage(content="<tool_call><function=update_lead_state>...</function></tool_call>Here is the real message.")
        mock_create.return_value = MockResponse([MockChoice(msg)])
        
        reply = await process_chat("test_agent_session", "Hello")
        assert "<tool_call>" not in reply
        assert "Here is the real message." in reply


@pytest.mark.asyncio
async def test_no_reasoning_leak():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        msg = MockMessage(content="I should inform the customer that the slot is full.\nHere is the real message.")
        mock_create.return_value = MockResponse([MockChoice(msg)])
        
        reply = await process_chat("test_agent_session", "Hello")
        assert "I should inform the customer" not in reply
        assert "Here is the real message." in reply


@pytest.mark.asyncio
async def test_human_escalation_ends_conversation():
    with patch("app.agent.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        tc = MockToolCall("call_1", MockToolFunction("request_human_callback", json.dumps({})))
        msg1 = MockMessage(content=None, tool_calls=[tc])
        msg2 = MockMessage(content="Passed to a human.")
        mock_create.side_effect = [MockResponse([MockChoice(msg1)]), MockResponse([MockChoice(msg2)])]
        
        reply = await process_chat("test_agent_session", "Call me")
        session = get_session("test_agent_session")
        assert session.lead_state.human_escalation is True
        assert session.conversation_ended is True
