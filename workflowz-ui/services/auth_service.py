from services.api_client import APIClient


def login(email: str, password: str) -> str:
    client = APIClient()
    response = client.post(
        "/api/auth/token",
        data={"username": email, "password": password},
    )
    return response.data["access_token"]
