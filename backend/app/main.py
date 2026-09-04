import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from openai import AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError, APIStatusError, BadRequestError
from .models import ChatRequest, ChatResponse, ResetRequest, ResetResponse, SessionData
from .session import get_session, reset_session
from .agent import process_chat
from .analytics import generate_analytics
from .config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Northstar AI Sales Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _handle_llm_error(exc: Exception, error_type: str):
    if settings.debug:
        status_code = getattr(exc, "status_code", 500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "LLM request failed", "error_type": error_type, "status_code": status_code}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the request right now."
        )

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if len(request.message) > settings.max_message_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is too long."
        )
    
    try:
        reply = await process_chat(request.session_id, request.message)
    except AuthenticationError as exc:
        logger.exception("LLM API authentication error: status_code=%s message=%s", getattr(exc, "status_code", None), getattr(exc, "body", None))
        _handle_llm_error(exc, "AuthenticationError")
    except RateLimitError as exc:
        logger.exception("LLM API rate limit error: status_code=%s message=%s", getattr(exc, "status_code", None), getattr(exc, "body", None))
        _handle_llm_error(exc, "RateLimitError")
    except BadRequestError as exc:
        logger.exception("LLM API bad request error: status_code=%s message=%s", getattr(exc, "status_code", None), getattr(exc, "body", None))
        _handle_llm_error(exc, "BadRequestError")
    except APIStatusError as exc:
        logger.exception("LLM API status error: status_code=%s message=%s", getattr(exc, "status_code", None), getattr(exc, "body", None))
        _handle_llm_error(exc, "APIStatusError")
    except APITimeoutError as exc:
        logger.exception("LLM API timeout error: message=%s", str(exc))
        _handle_llm_error(exc, "APITimeoutError")
    except APIConnectionError as exc:
        logger.exception("LLM API connection error: message=%s", str(exc))
        _handle_llm_error(exc, "APIConnectionError")
    except Exception as exc:
        logger.exception("Unexpected error while processing chat request")
        if settings.debug:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"detail": "LLM request failed", "error_type": type(exc).__name__, "message": str(exc)}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to process the request right now."
            )
        
    session = get_session(request.session_id)
    
    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        conversation_ended=session.conversation_ended
    )

@app.post("/reset", response_model=ResetResponse)
def reset(request: ResetRequest):
    reset_session(request.session_id)
    return ResetResponse(status="success")

@app.get("/session/{session_id}", response_model=SessionData)
def get_session_data(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@app.get("/analytics/{session_id}")
def get_analytics(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return generate_analytics(session)
