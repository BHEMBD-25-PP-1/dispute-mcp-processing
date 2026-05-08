import re

from app.core.logger import logger


ORDER_ID_PATTERN = r"(TXN-\d+|order[_\s-]?id[:=]?\s*\d+)"


def parse_dispute(text: str):

    order_id_match = re.search(ORDER_ID_PATTERN, text)
    order_id = order_id_match.group(0) if order_id_match else None
    logger.info(f"Parsed order_id: {order_id}")
    return {
        "order_id": order_id,
        "raw_text": text
    }