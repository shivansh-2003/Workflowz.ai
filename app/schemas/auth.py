from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: EmailStr | None = None
    is_superuser: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72, description="Password must be 8-72 characters (bcrypt limit)")
    is_superuser: bool = False


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_superuser: bool

    model_config = {"from_attributes": True}
