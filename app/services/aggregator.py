from app.services.parser import parse_dispute
from app.services.nlu import detect_service
from app.services.dispatcher import dispatch
from app.core.logger import logger



def process_dispute(text: str):
    logger.info("Starting dispute processing pipeline")
    parsed = parse_dispute(text)
    nlu = detect_service(text) or {}
    service = nlu.get("service")
    mcp_data = dispatch(service, parsed)

    return {
        "parsed": parsed,
        "nlu": nlu,
        "mcp": mcp_data
    }