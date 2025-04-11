# app.models.permission

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.role_has_permissions import RoleHasPermissions
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import Role

class Permission(Base, TimestampMixin, table=True):
    __tablename__ = "permissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., unique=True)

    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RoleHasPermissions
    )
