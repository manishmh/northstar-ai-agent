import uuid
from typing import Dict, Any

def request_human_callback() -> Dict[str, Any]:
    return {
        "success": True,
        "reference_id": f"HC-{uuid.uuid4().hex[:6].upper()}"
    }
