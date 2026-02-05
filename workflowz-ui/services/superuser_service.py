from services.api_client import APIClient


def list_organizations() -> list[dict]:
    client = APIClient()
    return client.get("/api/superuser/organizations/").data or []


def create_organization(payload: dict) -> dict:
    client = APIClient()
    return client.post("/api/superuser/organizations/", json=payload).data


def rename_organization(organization_name: str, new_name: str) -> dict:
    client = APIClient()
    return client.patch(
        f"/api/superuser/organizations/{organization_name}",
        json={"new_name": new_name},
    ).data


def change_organization_head(organization_name: str, new_head_email: str) -> dict:
    client = APIClient()
    return client.patch(
        f"/api/superuser/organizations/{organization_name}/head",
        json={"new_head_email": new_head_email},
    ).data
