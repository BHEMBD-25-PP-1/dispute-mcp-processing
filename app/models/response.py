from pydantic import BaseModel
from typing import Dict, Any


class DisputeResponse(BaseModel):
    parsed: Dict[str, Any]
    nlu: Dict[str, Any]
    mcp: Dict[str, Any]