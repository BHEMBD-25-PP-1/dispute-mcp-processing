import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GIGACHAT_AUTH_URL = os.getenv("GIGACHAT_AUTH_URL")
    GIGACHAT_API_URL = os.getenv("GIGACHAT_API_URL")
    GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

settings = Settings()