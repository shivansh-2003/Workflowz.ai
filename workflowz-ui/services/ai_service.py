"""AI workflow service — generate plan, clarification, approve, reject."""

from services.api_client import APIClient


def _params(org_name: str | None) -> dict | None:
    return {"organization_name": org_name} if org_name else None


def start_ai_pipeline(
    project_id: int,
    text_description: str | None = None,
    markdown_content: str | None = None,
    organization_name: str | None = None,
) -> dict:
    """Start AI pipeline. Returns {workflow_id, status}."""
    client = APIClient()
    payload = {}
    if text_description is not None:
        payload["text_description"] = text_description
    if markdown_content is not None:
        payload["markdown_content"] = markdown_content
    return client.post(
        f"/api/projects/{project_id}/ai/generate",
        json=payload,
        params=_params(organization_name),
    ).data


def get_ai_status(
    project_id: int,
    organization_name: str | None = None,
) -> dict:
    """Poll current AI workflow state."""
    client = APIClient()
    return client.get(
        f"/api/projects/{project_id}/ai/status",
        params=_params(organization_name),
    ).data


def get_ai_plan(
    project_id: int,
    organization_name: str | None = None,
) -> dict:
    """Get generated plan (when in HUMAN_APPROVAL state)."""
    client = APIClient()
    return client.get(
        f"/api/projects/{project_id}/ai/plan",
        params=_params(organization_name),
    ).data


def submit_clarification(
    project_id: int,
    answers: dict,
    organization_name: str | None = None,
) -> dict:
    """Submit clarification answers and resume pipeline."""
    client = APIClient()
    return client.post(
        f"/api/projects/{project_id}/ai/clarification",
        json={"answers": answers},
        params=_params(organization_name),
    ).data


def approve_plan(
    project_id: int,
    approved: bool = True,
    edits: list | None = None,
    organization_name: str | None = None,
) -> dict:
    """Approve plan and persist tasks."""
    client = APIClient()
    payload = {"approved": approved}
    if edits is not None:
        payload["edits"] = edits
    return client.post(
        f"/api/projects/{project_id}/ai/approve",
        json=payload,
        params=_params(organization_name),
    ).data


def reject_plan(
    project_id: int,
    organization_name: str | None = None,
) -> dict:
    """Reject the AI-generated plan."""
    client = APIClient()
    return client.post(
        f"/api/projects/{project_id}/ai/reject",
        params=_params(organization_name),
    ).data
