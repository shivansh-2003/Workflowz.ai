from pydantic import BaseModel, EmailStr


class TeamMemberCreate(BaseModel):
    name: str
    email: EmailStr
    designation: str | None = None
    position: str = "member"


class TeamMemberOut(BaseModel):
    organization_name: str
    member_id: int
    name: str
    email: EmailStr
    designation: str | None
    position: str

    model_config = {"from_attributes": True}
