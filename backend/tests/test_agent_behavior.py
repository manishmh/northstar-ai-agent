import pytest
from app.config import settings
from app.agent import process_chat
from app.session import reset_session

# We will run these tests only if there's a valid API key.
@pytest.fixture(autouse=True)
def setup_and_teardown():
    if not settings.openrouter_api_key or settings.openrouter_api_key == "dummy-key":
        pytest.skip("No valid OpenRouter API key provided.")
    reset_session("test_behavior_session")
    yield
    reset_session("test_behavior_session")

@pytest.mark.asyncio
async def test_discount_hallucination():
    reply = await process_chat("test_behavior_session", "Is there any discount or offer?")
    lower_reply = reply.lower()
    # It must not claim NO discount exists
    assert "no discount" not in lower_reply
    assert "no offer" not in lower_reply
    assert "koi discount nahi" not in lower_reply
    assert "koi offer nahi" not in lower_reply
    # It should state lack of confirmed information
    assert "don't have confirmed information" in lower_reply or "not available" in lower_reply or "sales representative" in lower_reply

@pytest.mark.asyncio
async def test_unsupported_amenity():
    reply = await process_chat("test_behavior_session", "Does it have a swimming pool?")
    lower_reply = reply.lower()
    # Should not say a flat 'no' or 'yes'
    assert "don't have confirmed information" in lower_reply or "confirmed information" in lower_reply
    assert "no, it does not" not in lower_reply
    assert "yes, it does" not in lower_reply

@pytest.mark.asyncio
async def test_one_question_qualification():
    # Turn 1
    reply1 = await process_chat("test_behavior_session", "3 BHK chahiye")
    # Count questions
    q_count1 = reply1.count("?")
    assert q_count1 <= 1, f"Expected at most 1 question, got {q_count1}. Reply: {reply1}"
    
    # Turn 2
    reply2 = await process_chat("test_behavior_session", "Mera budget 2 crore hai")
    q_count2 = reply2.count("?")
    assert q_count2 <= 1, f"Expected at most 1 question, got {q_count2}. Reply: {reply2}"

@pytest.mark.asyncio
async def test_no_repeated_information():
    reply = await process_chat("test_behavior_session", "I want a 3 BHK, budget 2 crore.")
    lower_reply = reply.lower()
    # Should not ask for budget or configuration
    assert "what is your budget" not in lower_reply
    assert "what budget" not in lower_reply
    assert "configuration" not in lower_reply

@pytest.mark.asyncio
async def test_language_switching():
    reply1 = await process_chat("test_behavior_session", "bhai 3 bhk chahiye")
    assert "hai" in reply1.lower() or "toh" in reply1.lower() or "bilkul" in reply1.lower() or "kya" in reply1.lower()
    
    reply2 = await process_chat("test_behavior_session", "speak English please")
    assert "english" in reply2.lower() or "sure" in reply2.lower() or "budget" in reply2.lower()
    # Check it is in English
    
    reply3 = await process_chat("test_behavior_session", "budget 2 crore hai")
    # Should switch back to Hinglish/Hindi
    assert "hai" in reply3.lower() or "toh" in reply3.lower() or "kya" in reply3.lower() or "aap" in reply3.lower()

@pytest.mark.asyncio
async def test_unsupported_configuration():
    reply = await process_chat("test_behavior_session", "1 BHK chahiye, budget 1 crore hai")
    lower_reply = reply.lower()
    assert "1 bhk" in lower_reply
    assert "2 bhk" in lower_reply
    assert "3 bhk" in lower_reply
    # Should not be overly verbose (e.g. less than 400 chars)
    assert len(reply) < 400, f"Reply too verbose: {reply}"
