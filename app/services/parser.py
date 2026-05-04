import re


def parse_dispute(text: str):
    order_id = re.search(r"order_id=([A-Z0-9\-]+)", text)
    txn_id = re.search(r"txn_id=([A-Z0-9\-]+)", text)

    return {
        "order_id": order_id.group(1) if order_id else None,
        "txn_id": txn_id.group(1) if txn_id else None
    }