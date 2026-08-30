from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    role: UserRole = UserRole.user


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
