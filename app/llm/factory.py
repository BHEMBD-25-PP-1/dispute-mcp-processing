from app.core.config import gigaChatProperties
from app.llm.gigachat import GigaChatClient


def get_llm_client():

    if gigaChatProperties.LLM_PROVIDER == "gigachat":
        return GigaChatClient()

    raise ValueError("Unsupported LLM provider")