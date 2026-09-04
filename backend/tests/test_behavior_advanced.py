import pytest
from app.config import settings
from app.agent import process_chat
from app.session import reset_session, get_session

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if not settings.openrouter_api_key or settings.openrouter_api_key == "dummy-key":
        pytest.skip("No valid OpenRouter API key provided.")
    reset_session("test_advanced_session")
    yield
    reset_session("test_advanced_session")

@pytest.mark.asyncio
async def test_name_extraction():
    await process_chat("test_advanced_session", "Hi, my name is Manish.")
    session = get_session("test_advanced_session")
    assert session.lead_state.name.lower() == "manish"

@pytest.mark.asyncio
async def test_multiple_lead_fields():
    await process_chat("test_advanced_session", "My budget is 2 crore and I am currently in Bengaluru.")
    session = get_session("test_advanced_session")
    assert "2 cr" in session.lead_state.budget.lower() or "2 crore" in session.lead_state.budget.lower()
    assert "bengaluru" in session.lead_state.current_location.lower() or "bangalore" in session.lead_state.current_location.lower()

@pytest.mark.asyncio
async def test_multiple_fields_plus_booking():
    await process_chat("test_advanced_session", "Saturday at 11 AM works. My budget is 2 crore and I'm from Bengaluru.")
    session = get_session("test_advanced_session")
    assert session.lead_state.budget is not None
    assert session.lead_state.current_location is not None
    assert session.lead_state.site_visit_requested is True

@pytest.mark.asyncio
async def test_name_plus_booking():
    await process_chat("test_advanced_session", "I'm Manish and I'd like to visit Saturday at 11 AM.")
    session = get_session("test_advanced_session")
    assert session.lead_state.name is not None
    assert "manish" in session.lead_state.name.lower()
    assert session.lead_state.site_visit_requested is True

@pytest.mark.asyncio
async def test_dont_ask_name_unnecessarily():
    reply = await process_chat("test_advanced_session", "What is the price of a 2 BHK?")
    lower_reply = reply.lower()
    assert "name" not in lower_reply
    assert "may i know" not in lower_reply

@pytest.mark.asyncio
async def test_contact_details_extraction():
    await process_chat("test_advanced_session", "My email is test@example.com and phone is 9876543210.")
    session = get_session("test_advanced_session")
    assert session.lead_state.email == "test@example.com"
    assert session.lead_state.phone == "9876543210"
