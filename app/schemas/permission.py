from datetime import datetime
from pydantic import BaseModel

class PermissionBase(BaseModel):
    name: str

class PermissionRead(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
