import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Password must contain at least one letter and one number")
        return v

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Password must contain at least one letter and one number")
        return v


class AnalysisRequest(BaseModel):
    resume_id: int
    job_title: Optional[str] = Field(default=None, max_length=255)
    job_description: str = Field(min_length=30, max_length=30000)


class SkillExtractRequest(BaseModel):
    text: str = Field(min_length=3, max_length=50000)


class AdminUserUpdate(BaseModel):
    role: Optional[str] = Field(default=None, pattern="^(user|admin)$")
    is_active: Optional[bool] = None
