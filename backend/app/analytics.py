from .models import SessionData
from typing import Dict, Any

def generate_analytics(session: SessionData) -> Dict[str, Any]:
    return {
        "lead_summary": {
            "name": session.lead_state.name,
            "configuration": session.lead_state.configuration,
            "budget": session.lead_state.budget,
            "purpose": session.lead_state.purpose,
            "current_location": session.lead_state.current_location,
            "purchase_timeline": session.lead_state.purchase_timeline,
            "interest_level": session.lead_state.interest_level,
            "site_visit_requested": session.lead_state.site_visit_requested,
            "site_visit_status": session.lead_state.site_visit_status,
            "follow_up_required": session.lead_state.follow_up_required,
            "human_escalation": session.lead_state.human_escalation,
            "contact_permission": session.lead_state.contact_permission
        },
        "conversation": {
            "language": session.lead_state.language,
            "message_count": session.message_count,
            "conversation_outcome": session.lead_state.conversation_outcome
        }
    }
