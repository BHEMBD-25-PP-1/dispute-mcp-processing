from fastapi import APIRouter

from app.services.parser import parse_dispute
from app.services.nlu import detect_service
from app.services.dispatcher import dispatch
from app.services.aggregator import build_response

router = APIRouter()


@router.post("/dispute")
def handle_dispute(payload: dict):

    text = payload.get("text")

    parsed = parse_dispute(text)

    nlu = detect_service(text)

    mcp_data = dispatch(nlu["service"], parsed)

    return build_response(parsed, nlu, mcp_data)