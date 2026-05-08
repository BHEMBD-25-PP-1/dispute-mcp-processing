from fastapi import APIRouter
from app.core.logger import logger
from app.models.request import DisputeRequest
from app.models.response import DisputeResponse
from app.services.aggregator import process_dispute


router = APIRouter()


@router.post("/dispute", response_model=DisputeResponse)
def handle_dispute(request: DisputeRequest):
    logger.info(f"New dispute received: {request.text}")
    result = process_dispute(request.text)
    return result