# app/models/user.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.data_source import DataSource

class User(Base, TimestampMixin, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., nullable=False)
    email: str = Field(..., nullable=False, unique=True)
    password: str = Field(..., nullable=False)
    status: str = Field(default="active", nullable=False)
    
    # Foreign key to Role
    role_id: Optional[int] = Field(default=None, foreign_key="roles.id")

    # Relationship to Role
    role: "Role" = Relationship(back_populates="users")

    # Relationship to DataSource
    data_sources: List["DataSource"] = Relationship(back_populates="created_by")
