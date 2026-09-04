import pytest
from app.config import settings
from app.agent import process_chat
from app.session import reset_session, get_session
import json

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if not settings.openrouter_api_key or settings.openrouter_api_key == "dummy-key":
        pytest.skip("No valid OpenRouter API key provided.")
    reset_session("test_booking_val")
    yield
    reset_session("test_booking_val")

@pytest.mark.asyncio
async def test_booking_rejected_date_time_only():
    # Attempt to book site visit directly without providing any contact details
    await process_chat("test_booking_val", "I want to visit this Saturday at 11 AM.")
    session = get_session("test_booking_val")
    assert session.lead_state.site_visit_status != "booked"
    assert session.lead_state.booking_reference is None

@pytest.mark.asyncio
async def test_booking_rejected_missing_phone_email():
    # Provide name, but missing phone and email
    await process_chat("test_booking_val", "I am Manish. I want to visit this Saturday at 11 AM.")
    session = get_session("test_booking_val")
    assert session.lead_state.site_visit_status != "booked"
    assert session.lead_state.booking_reference is None

@pytest.mark.asyncio
async def test_booking_rejected_missing_email():
    # Provide name and phone, but missing email
    await process_chat("test_booking_val", "I am Manish, my phone is 9006222269. I want to visit this Saturday at 11 AM.")
    session = get_session("test_booking_val")
    assert session.lead_state.site_visit_status != "booked"
    assert session.lead_state.booking_reference is None

@pytest.mark.asyncio
async def test_booking_allowed_all_contact_details():
    # Provide name, phone, and email
    await process_chat("test_booking_val", "I am Manish, my phone is 9006222269, and email is manishmh@gmail.com. I want to visit this Saturday at 11 AM.")
    session = get_session("test_booking_val")
    assert session.lead_state.site_visit_status == "booked"
    assert session.lead_state.booking_reference is not None
    assert session.lead_state.name.lower() == "manish"

@pytest.mark.asyncio
async def test_booking_allowed_with_configuration():
    # Provide all contact details and configuration
    await process_chat("test_booking_val", "I am Manish, my phone is 9006222269, email manishmh@gmail.com, looking for a 2 BHK. I want to visit this Saturday at 11 AM.")
    session = get_session("test_booking_val")
    assert session.lead_state.site_visit_status == "booked"
    assert session.lead_state.booking_reference is not None
    assert session.lead_state.configuration == "2 BHK"

@pytest.mark.asyncio
async def test_booking_failure_never_sets_status_booked():
    # Provide all contact details but invalid slot
    await process_chat("test_booking_val", "I am Manish, my phone is 9006222269, email manishmh@gmail.com, looking for a 2 BHK. I want to visit next year.")
    session = get_session("test_booking_val")
    assert session.lead_state.site_visit_status != "booked"
    assert session.lead_state.booking_reference is None
