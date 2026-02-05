from services.api_client import APIClient


def list_tasks(
    project_id: int, organization_name: str | None = None
) -> list[dict]:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.get(f"/api/projects/{project_id}/tasks", params=params).data or []


def create_task(project_id: int, payload: dict, organization_name: str | None = None) -> dict:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.post(
        f"/api/projects/{project_id}/tasks",
        json=payload,
        params=params,
    ).data


def update_task(
    project_id: int, task_id: int, payload: dict, organization_name: str | None = None
) -> dict:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.patch(
        f"/api/projects/{project_id}/tasks/{task_id}",
        json=payload,
        params=params,
    ).data


def complete_task(
    project_id: int, task_id: int, completed: bool, organization_name: str | None = None
) -> dict:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    return client.patch(
        f"/api/projects/{project_id}/tasks/{task_id}/complete",
        json={"task_completed": completed},
        params=params,
    ).data


def delete_task(
    project_id: int, task_id: int, organization_name: str | None = None
) -> None:
    client = APIClient()
    params = {"organization_name": organization_name} if organization_name else None
    client.delete(f"/api/projects/{project_id}/tasks/{task_id}", params=params)
