# app/schemas/data_source.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.data_source import SourceType
from app.schemas.grafana_source import GrafanaSourceRead
from app.schemas.kibana_source import KibanaSourceRead

class DataSourceBase(BaseModel):
    type: SourceType
    name: str
    description: Optional[str] = None
    status: Optional[str] = None

class DataSourceCreate(DataSourceBase):
    """
    Fields for creating a DataSource.
    No need for created_by_id, that will be automatically
    set from the current user in the create endpoint.
    """
    pass

class DataSourceRead(DataSourceBase):
    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    grafana_sources: List[GrafanaSourceRead] = []
    kibana_sources: List[KibanaSourceRead] = []

    class Config:
        from_attributes = True

class DataSourceUpdate(BaseModel):
    type: Optional[SourceType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
