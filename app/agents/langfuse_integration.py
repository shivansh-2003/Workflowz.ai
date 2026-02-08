"""Langfuse integration for agent observability."""

import os
from pathlib import Path
from typing import Any

_path = Path(__file__).resolve().parent / ".env"
if _path.exists():
    from dotenv import load_dotenv
    load_dotenv(_path)
if not os.environ.get("LANGFUSE_HOST") and os.environ.get("LANGFUSE_BASE_URL"):
    os.environ["LANGFUSE_HOST"] = os.environ["LANGFUSE_BASE_URL"]

from app.core.config import settings

_LANGFUSE_CLIENT: Any = None
_LANGFUSE_HANDLER: Any = None


def get_langfuse_client() -> Any:
    """Return Langfuse client."""
    global _LANGFUSE_CLIENT
    if _LANGFUSE_CLIENT is None:
        from langfuse import Langfuse
        _LANGFUSE_CLIENT = Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_BASE_URL,
        )
    return _LANGFUSE_CLIENT


def get_langfuse_handler() -> Any:
    """Return Langfuse CallbackHandler for LangChain."""
    global _LANGFUSE_HANDLER
    if _LANGFUSE_HANDLER is None:
        from langfuse.langchain import CallbackHandler
        _LANGFUSE_HANDLER = CallbackHandler()
    return _LANGFUSE_HANDLER


def flush() -> None:
    """Flush Langfuse client to ensure traces are sent."""
    get_langfuse_client().flush()


def get_runnable_config(run_name: str = "orchestrator") -> dict[str, Any]:
    """Return LangChain RunnableConfig with Langfuse callbacks."""
    return {"callbacks": [get_langfuse_handler()], "run_name": run_name}
