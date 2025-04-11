# app/models/grafana_source.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from enum import Enum
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.data_source import DataSource

class AuthType(str, Enum):
    BASIC = "basic"
    BEARER = "bearer"
    
    @classmethod
    def _missing_(cls, value: object) -> Optional["AuthType"]:
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
    
class GrafanaSource(Base, TimestampMixin, table=True):
    __tablename__ = "grafana_sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    data_source_id: int = Field(foreign_key="data_sources.id")

    source_url: str = Field(..., nullable=False)

    # Use the enum as a "string" type in the DB
    auth_type: AuthType = Field(..., nullable=False)

    # For BASIC:
    auth_username: Optional[str] = Field(default=None)
    auth_password: Optional[str] = Field(default=None)  # used only if auth_type == AuthType.BASIC

    # For Bearer Tokens:
    bearer_token: Optional[str] = Field(default=None)  # used only if auth_type == AuthType.BEARER

    # Relationship to DataSource
    data_source: "DataSource" = Relationship(back_populates="grafana_sources")

