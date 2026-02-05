from services.api_client import APIClient


def list_projects(organization_name: str | None = None) -> list[dict]:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.get("/api/projects", params=params).data or []


def create_project(
    project_name: str,
    project_description: str | None,
    organization_name: str | None = None,
) -> dict:
    client = APIClient()
    payload = {"project_name": project_name, "project_description": project_description}
    params = {"organization_name": organization_name} if organization_name else None
    return client.post("/api/projects", json=payload, params=params).data


def update_project(
    project_id: int,
    data: dict,
    organization_name: str | None = None,
) -> dict:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.patch(f"/api/projects/{project_id}", json=data, params=params).data


def delete_project(project_id: int, organization_name: str | None = None) -> None:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    client.delete(f"/api/projects/{project_id}", params=params)
