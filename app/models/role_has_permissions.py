# app.models.role_has_permissions

from typing import Optional
from sqlmodel import Field
from app.db.base import Base

class RoleHasPermissions(Base, table=True):
    __tablename__ = "role_has_permissions"
    role_id: Optional[int] = Field(
        default=None,
        foreign_key="roles.id",
        primary_key=True
    )
    permission_id: Optional[int] = Field(
        default=None,
        foreign_key="permissions.id",
        primary_key=True
    )
