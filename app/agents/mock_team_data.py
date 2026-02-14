"""Mock team data for testing when database is unavailable."""

MOCK_TEAMS = {
    "bajaj-finserv": [
        {
            "organization_name": "bajaj-finserv",
            "member_id": 1,
            "name": "Rajesh Kumar",
            "email": "rajesh.kumar@bajaj.com",
            "designation": "backend",
            "position": "head"
        },
        {
            "organization_name": "bajaj-finserv",
            "member_id": 2,
            "name": "Priya Sharma",
            "email": "priya.sharma@bajaj.com",
            "designation": "frontend",
            "position": "member"
        },
        {
            "organization_name": "bajaj-finserv",
            "member_id": 3,
            "name": "Amit Patel",
            "email": "amit.patel@bajaj.com",
            "designation": "backend",
            "position": "member"
        },
        {
            "organization_name": "bajaj-finserv",
            "member_id": 4,
            "name": "Sneha Reddy",
            "email": "sneha.reddy@bajaj.com",
            "designation": "qa",
            "position": "member"
        }
    ],
    "techcorp": [
        {
            "organization_name": "techcorp",
            "member_id": 1,
            "name": "John Doe",
            "email": "john@techcorp.com",
            "designation": "backend",
            "position": "head"
        },
        {
            "organization_name": "techcorp",
            "member_id": 2,
            "name": "Jane Smith",
            "email": "jane@techcorp.com",
            "designation": "frontend",
            "position": "member"
        }
    ]
}

def get_mock_team(organization_name: str) -> list[dict]:
    """Get mock team data for an organization."""
    return MOCK_TEAMS.get(organization_name.lower(), [])
