from langchain_ollama import ChatOllama

from app.core.config import settings


def get_chat_model() -> ChatOllama:
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.2,
    )