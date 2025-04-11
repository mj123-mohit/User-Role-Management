from sqlmodel import SQLModel, Field
from datetime import datetime, UTC

class Base(SQLModel):
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_row_format": "DYNAMIC"}

class TimestampMixin:
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

