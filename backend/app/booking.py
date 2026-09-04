import uuid
from typing import Dict, Any

AVAILABLE_SLOTS = [
    "Saturday 11:00 AM",
    "Saturday 2:00 PM",
    "Sunday 11:00 AM",
    "Sunday 4:00 PM"
]

def book_site_visit(date: str, time: str) -> Dict[str, Any]:
    requested_slot = f"{date} {time}"
    # Very simple deterministic match
    if any(requested_slot.lower() == slot.lower() for slot in AVAILABLE_SLOTS):
        return {
            "success": True,
            "date": date,
            "time": time,
            "booking_id": f"NS-{uuid.uuid4().hex[:6].upper()}"
        }
    else:
        return {
            "success": False,
            "error": "slot_unavailable",
            "message": "The requested slot is unavailable.",
            "alternatives": AVAILABLE_SLOTS
        }
