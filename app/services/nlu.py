from app.llm.factory import get_llm_client
from app.core.logger import logger
from app.llm.prompts import DISPUTE_CLASSIFIER_PROMPT


def build_prompt(text: str):
    return DISPUTE_CLASSIFIER_PROMPT.format(text=text)


def detect_service(text: str):
    client = get_llm_client()
    response = client.chat(build_prompt(text))
    service = response.strip().lower()
    logger.info(f"Detected service: {service}")
    return {
        "service": service
    }