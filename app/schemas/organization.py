from pydantic import BaseModel, EmailStr


class OrganizationCreate(BaseModel):
    organization_name: str
    head_email: EmailStr
    head_name: str
    head_designation: str | None = None


class OrganizationRename(BaseModel):
    new_name: str


class OrganizationHeadUpdate(BaseModel):
    new_head_email: EmailStr


class OrganizationOut(BaseModel):
    organization_name: str
    head_name: str | None = None
    head_email: str | None = None
    member_count: int = 0
