import uuid
import requests
from app.core.config import gigaChatProperties
from app.llm.base import BaseLLMClient


class GigaChatClient(BaseLLMClient):

    def __init__(self):
        self.token = self._get_token()

    def _get_token(self):

        headers = {
            "Authorization": f"Basic {gigaChatProperties.GIGACHAT_AUTH_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4())
        }

        data = {
            "scope": "GIGACHAT_API_PERS"
        }

        response = requests.post(
            gigaChatProperties.GIGACHAT_AUTH_URL,
            headers=headers,
            data=data,
            verify=False
        )

        response.raise_for_status()

        return response.json()["access_token"]

    def chat(self, prompt: str):

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0
        }

        response = requests.post(
            gigaChatProperties.GIGACHAT_API_URL,
            headers=headers,
            json=payload,
            verify=False
        )

        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]