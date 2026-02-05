import os

from dotenv import load_dotenv

load_dotenv()


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000")
