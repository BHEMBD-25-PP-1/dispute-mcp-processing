from app.llm.gigachat import GigaChatClient
from app.core.llm_config import get_gigachat_settings

gigachat_settings = get_gigachat_settings()

def get_llm_client():

    if gigachat_settings.LLM_PROVIDER == "gigachat":
        return GigaChatClient()

    raise ValueError("Unsupported LLM provider")