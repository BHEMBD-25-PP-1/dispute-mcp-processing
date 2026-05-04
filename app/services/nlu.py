import json
from app.mcp.gigachat import GigaChatClient


def build_prompt(text: str):
    return f"""
Ты классификатор диспутов НСПК.

Определи сервис:

- taxi
- afisha

Ответ ТОЛЬКО JSON:
{{
  "service": "taxi | afisha"
}}

Запрос:
{text}
"""


def detect_service(text: str):
    client = GigaChatClient()

    response = client.chat(build_prompt(text))

    try:
        return json.loads(response)
    except:
        return {"service": "unknown"}