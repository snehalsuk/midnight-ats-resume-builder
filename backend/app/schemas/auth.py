from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.resume import _to_camel


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = ""
    last_name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=_to_camel)

    id: int
    email: str
    first_name: str
    last_name: str
