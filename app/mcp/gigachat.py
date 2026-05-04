import requests
import base64
from app.core.config import settings
import uuid 



class GigaChatClient:
    def __init__(self):
        self.token = self._get_token()

    def _get_token(self):

        headers = {
            "Authorization": f"Basic {settings.GIGACHAT_AUTH_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4())
        }

        data = {
            "scope": "GIGACHAT_API_PERS"
        }

        r = requests.post(
            settings.GIGACHAT_AUTH_URL,
            headers=headers,
            data=data,
            verify=False
        )

        print("STATUS:", r.status_code)
        print("BODY:", r.text)

        r.raise_for_status()

        return r.json()["access_token"]

    def chat(self, prompt: str):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }

        r = requests.post(settings.GIGACHAT_API_URL, headers=headers, json=payload, verify=False)
        r.raise_for_status()

        return r.json()["choices"][0]["message"]["content"]