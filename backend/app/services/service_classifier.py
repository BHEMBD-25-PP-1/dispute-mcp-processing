from app.core.logger import logger
from app.llm.prompts import DISPUTE_CLASSIFIER_PROMPT


SERVICE_KEYWORDS = {
    "taxi": ("taxi", "такси", "поездк", "маршрут", "водител", "машин"),
    "afisha": ("afisha", "афиша", "билет", "событи", "концерт", "театр", "qr"),
}


def build_prompt(text: str):
    return DISPUTE_CLASSIFIER_PROMPT.format(text=text)


def get_llm_client():
    from app.llm.factory import get_llm_client as factory_get_llm_client

    return factory_get_llm_client()


def detect_service(text: str, service_hint: str | None = None):
    if service_hint in {"taxi", "afisha"}:
        return {"service": service_hint, "confidence": 98, "source": "explicit_hint"}

    normalized = text.lower()
    scores = {
        service: sum(1 for keyword in keywords if keyword in normalized)
        for service, keywords in SERVICE_KEYWORDS.items()
    }
    best_service, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        confidence = min(94, 58 + best_score * 12)
        logger.info("Detected service by rules: %s", best_service)
        return {"service": best_service, "confidence": confidence, "source": "rules"}

    try:
        client = get_llm_client()
        response = client.chat(build_prompt(text))
    except Exception as exc:
        logger.warning("LLM service detection skipped: %s", exc)
        return {"service": "unknown", "confidence": 35, "source": "fallback"}

    if not response:
        logger.error("Empty LLM response")
        return {"service": "unknown", "confidence": 35, "source": "llm"}

    service = str(response).strip().lower()
    if service not in {"taxi", "afisha"}:
        service = "unknown"
    logger.info("Detected service by LLM: %s", service)
    return {
        "service": service,
        "confidence": 82 if service != "unknown" else 35,
        "source": "llm",
    }
