import hashlib
import json


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def build_request_hash(text: str) -> str:
    payload = {"text": normalize_text(text)}
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
