# app/models/data_source.py

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.db.base import Base, TimestampMixin
from enum import Enum

if TYPE_CHECKING:
    from app.models.kibana_source import KibanaSource
    from app.models.grafana_source import GrafanaSource
    from app.models.user import User

class SourceType(str, Enum):
    GRAFANA = "grafana"
    KIBANA = "kibana"

    @classmethod
    def _missing_(cls, value: object) -> Optional["SourceType"]:
        """
        Called by Enum when a value is not found among existing members.
        We override this to allow case-insensitive matching.
        """
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        return None

class DataSource(Base, TimestampMixin, table=True):
    __tablename__ = "data_sources"
    id: Optional[int] = Field(default=None, primary_key=True)
    type: SourceType = Field(..., nullable=False)
    name: str = Field(..., nullable=False)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    created_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships
    kibana_sources: List["KibanaSource"] = Relationship(back_populates="data_source")
    grafana_sources: List["GrafanaSource"] = Relationship(back_populates="data_source")

    # Relationship to User
    created_by: "User" = Relationship(back_populates="data_sources")


