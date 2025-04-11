# app/schemas/kibana_source.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, model_validator
from app.models.kibana_source import AuthType

class KibanaSourceBase(BaseModel):
    source_url: str
    auth_type: AuthType

class KibanaSourceCreate(KibanaSourceBase):
    """
    Fields for creating a KibanaSource.
    data_source_id must be provided in the endpoint
    (e.g., as a path or form input), or you can add it here if you prefer.
    """
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    bearer_token: Optional[str] = None
    data_source_id: int

    @model_validator(mode='after')
    def validate_auth_fields(self):
        """
        Ensures that only relevant authentication fields are populated based on auth_type.
        """
        if self.auth_type == AuthType.BASIC:
            if not self.auth_username or not self.auth_password:
                raise ValueError("auth_username and auth_password must be set for BASIC auth")
            if self.bearer_token:
                raise ValueError("bearer_token should not be set for BASIC auth")
        elif self.auth_type == AuthType.BEARER:
            if not self.bearer_token:
                raise ValueError("bearer_token must be set for BEARER auth")
            if self.auth_username or self.auth_password:
                raise ValueError("auth_username and auth_password should not be set for BEARER auth")
        else:
            raise ValueError("Invalid auth_type provided")
        return self

class KibanaSourceRead(KibanaSourceBase):
    id: int
    data_source_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class KibanaSourceUpdate(BaseModel):
    source_url: Optional[str] = None
    data_source_id: Optional[int] = None
    auth_type: Optional[AuthType] = None
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    bearer_token: Optional[str] = None

    @model_validator(mode='after')
    def validate_auth_fields(self):
        """
        Ensures that only relevant authentication fields are populated based on auth_type.
        """
        if self.auth_type == AuthType.BASIC:
            if not self.auth_username or not self.auth_password:
                raise ValueError("auth_username and auth_password must be set for BASIC auth")
            if self.bearer_token:
                raise ValueError("bearer_token should not be set for BASIC auth")
        elif self.auth_type == AuthType.BEARER:
            if not self.bearer_token:
                raise ValueError("bearer_token must be set for BEARER auth")
            if self.auth_username or self.auth_password:
                raise ValueError("auth_username and auth_password should not be set for BEARER auth")
        else:
            raise ValueError("Invalid auth_type provided")
        return self
