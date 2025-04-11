from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.permission import PermissionRead

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None

class RoleRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionRead] = []

    class Config:
        from_attributes = True

