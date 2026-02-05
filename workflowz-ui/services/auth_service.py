from services.api_client import APIClient


def login(email: str, password: str) -> str:
    client = APIClient()
    response = client.post(
        "/api/auth/token",
        data={"username": email, "password": password},
    )
    return response.data["access_token"]


def signup(email: str, password: str) -> dict:
    """Public signup - first user becomes superuser automatically."""
    client = APIClient()
    response = client.post(
        "/api/auth/signup",
        json={"email": email, "password": password, "is_superuser": False},
    )
    return response.data


def register_user(email: str, password: str, is_superuser: bool = False) -> dict:
    """Superuser-only: Create a new user account."""
    client = APIClient()
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "is_superuser": is_superuser},
    )
    return response.data
