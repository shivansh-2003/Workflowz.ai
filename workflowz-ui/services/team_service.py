from services.api_client import APIClient


def list_members(organization_name: str | None = None) -> list[dict]:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.get("/api/teams", params=params).data or []


def add_member(payload: dict, organization_name: str | None = None) -> dict:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.post("/api/teams", json=payload, params=params).data
