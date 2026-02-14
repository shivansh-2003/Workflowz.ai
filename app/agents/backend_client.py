"""Backend API client for fetching data from FastAPI server."""

import logging
from typing import Any

import httpx

from app.agents.utils import build_team_capability_model
from app.core.config import settings

logger = logging.getLogger(__name__)

# Backend URL (adjust if needed)
BACKEND_URL = f"http://localhost:8000{settings.API_V1_PREFIX}"


async def fetch_team_capability_model(
    organization_name: str,
    auth_token: str | None = None,
) -> dict[str, Any]:
    """
    Fetch team members from backend and convert to team capability model.

    Args:
        organization_name: Organization to fetch team for
        auth_token: Optional JWT token for authentication

    Returns:
        Team capability model: { team_size, capabilities, missing_capabilities, load_capacity }
    """
    # Use internal endpoint (no auth required) if no token provided
    if auth_token:
        url = f"{BACKEND_URL}/teams/"
        params = {"organization_name": organization_name}
        headers = {"Authorization": f"Bearer {auth_token}"}
    else:
        url = f"{BACKEND_URL}/teams/internal/capability-model"
        # Use mock data when database is unavailable
        params = {"organization_name": organization_name, "use_mock": "true"}
        headers = {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            team_members_data = response.json()

        # Convert TeamMemberOut to format expected by build_team_capability_model
        # TeamMemberOut: { organization_name, member_id, name, email, designation, position }
        # Expected: [{ member_id, designation, seniority }]
        
        # Map designation to seniority (simple heuristic for now)
        team_members = []
        for member in team_members_data:
            # Use designation if available, otherwise infer from position
            designation = member.get("designation")
            if not designation:
                # If no designation, use position
                designation = "head" if member.get("position") == "head" else "backend"
            
            # Simple seniority mapping (can be enhanced)
            # For now, heads are senior, members are mid
            seniority = "senior" if member.get("position") == "head" else "mid"
            
            team_members.append({
                "member_id": member["member_id"],
                "designation": designation,
                "seniority": seniority,
            })

        logger.info(
            "BackendClient:fetch_team_capability_model fetched %d members for org=%s",
            len(team_members),
            organization_name,
        )
        return build_team_capability_model(team_members)

    except httpx.HTTPStatusError as e:
        logger.error(
            "BackendClient:http_error status=%d url=%s",
            e.response.status_code,
            url,
        )
        # Return empty capability model on error
        return build_team_capability_model([])
    except httpx.RequestError as e:
        logger.error("BackendClient:request_error %s", e)
        # Return empty capability model on error
        return build_team_capability_model([])
    except Exception as e:
        logger.exception("BackendClient:unexpected_error")
        # Return empty capability model on error
        return build_team_capability_model([])


def fetch_team_capability_model_sync(
    organization_name: str,
    auth_token: str | None = None,
) -> dict[str, Any]:
    """
    Synchronous wrapper for fetch_team_capability_model.
    Used in orchestrator (which runs synchronously).
    """
    # Use internal endpoint (no auth required) if no token provided
    if auth_token:
        url = f"{BACKEND_URL}/teams/"
        params = {"organization_name": organization_name}
        headers = {"Authorization": f"Bearer {auth_token}"}
    else:
        url = f"{BACKEND_URL}/teams/internal/capability-model"
        # Use mock data when database is unavailable
        params = {"organization_name": organization_name, "use_mock": "true"}
        headers = {}

    try:
        logger.info("BackendClient:fetch_team url=%s params=%s", url, params)
        response = httpx.get(url, params=params, headers=headers, timeout=10.0)
        response.raise_for_status()
        team_members_data = response.json()
        logger.info("BackendClient:fetch_team received %d members", len(team_members_data))

        team_members = []
        for member in team_members_data:
            designation = member.get("designation")
            if not designation:
                designation = "head" if member.get("position") == "head" else "backend"
            
            seniority = "senior" if member.get("position") == "head" else "mid"
            
            team_members.append({
                "member_id": member["member_id"],
                "designation": designation,
                "seniority": seniority,
            })

        logger.info(
            "BackendClient:fetch_team_capability_model_sync fetched %d members for org=%s",
            len(team_members),
            organization_name,
        )
        return build_team_capability_model(team_members)

    except httpx.HTTPStatusError as e:
        logger.error(
            "BackendClient:http_error status=%d url=%s response=%s",
            e.response.status_code,
            url,
            e.response.text[:200] if hasattr(e.response, 'text') else "N/A",
        )
        return build_team_capability_model([])
    except httpx.RequestError as e:
        logger.error("BackendClient:request_error url=%s error=%s", url, str(e))
        return build_team_capability_model([])
    except Exception as e:
        logger.exception("BackendClient:unexpected_error")
        return build_team_capability_model([])
