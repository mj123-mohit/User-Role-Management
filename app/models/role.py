# app.models.role

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.role_has_permissions import RoleHasPermissions
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.permission import Permission

class Role(Base, TimestampMixin, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., unique=True)

    # relationships
    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RoleHasPermissions
    )
