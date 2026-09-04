from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    conversation_ended: bool

class ResetRequest(BaseModel):
    session_id: str

class ResetResponse(BaseModel):
    status: str

class LeadState(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    configuration: Optional[str] = None
    budget: Optional[str] = None
    purpose: Optional[str] = None
    current_location: Optional[str] = None
    purchase_timeline: Optional[str] = None
    interest_level: Optional[str] = None
    site_visit_requested: Optional[bool] = None
    site_visit_status: Optional[str] = None
    site_visit_date: Optional[str] = None
    site_visit_time: Optional[str] = None
    booking_reference: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_time: Optional[str] = None
    human_escalation: Optional[bool] = None
    contact_permission: Optional[bool] = None
    conversation_outcome: Optional[str] = None
    language: Optional[str] = None

class SessionData(BaseModel):
    session_id: str
    conversation_history: List[Dict[str, Any]] = []
    lead_state: LeadState = Field(default_factory=LeadState)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    conversation_ended: bool = False
    message_count: int = 0
