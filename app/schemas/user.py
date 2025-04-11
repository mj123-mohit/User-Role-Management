# app/schemas/user.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.models.role import Role

class UserBase(BaseModel):
    name: str
    email: EmailStr
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "editor"

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    role: str

    @field_validator("role", mode="before")
    def extract_role_name(cls, v):
        # If v is actually a Role object, replace it with v.name
        if isinstance(v, Role):
            return v.name
        return v

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    role: Optional[str] = None

class UserPermissions(UserBase):
    id: int
    role: Role 
    permissions: list[str] = []

    class Config:
        from_attributes = True

