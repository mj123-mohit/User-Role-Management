# app/api/v1/endpoints/grafana_sources.py

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from datetime import datetime, UTC

from app.api.deps import get_db_session, format_source_url, user_has_permission
from app.schemas.grafana_source import (
    GrafanaSourceCreate,
    GrafanaSourceRead,
    GrafanaSourceUpdate,
)
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse
from app.models.grafana_source import GrafanaSource
from app.models.data_source import DataSource

router = APIRouter()

@router.get("/", response_model=SuccessResponse)
def read_grafana_sources(
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_grafana_source")),
):
    """List all Grafana sources."""
    grafana_sources = db.exec(select(GrafanaSource)).all()
    pydantic_grafana_sources = [
        GrafanaSourceRead.model_validate(gs) for gs in grafana_sources
    ]

    result = {"grafana_sources": pydantic_grafana_sources}
    return ResponseController.send_response(
        result=result,
        message="List of Grafana sources",
        code=status.HTTP_200_OK
    )

@router.get("/{grafana_source_id}", response_model=SuccessResponse)
def read_grafana_source(
    grafana_source_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_grafana_source")),
):
    """Retrieve a single Grafana source by its ID."""
    grafana_source = db.get(GrafanaSource, grafana_source_id)
    if not grafana_source:
        return ResponseController.send_error(
            error="Grafana source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    pydantic_grafana_source = GrafanaSourceRead.model_validate(grafana_source)
    result = {"grafana_source": pydantic_grafana_source}

    return ResponseController.send_response(
        result=result,
        message="Grafana source details",
        code=status.HTTP_200_OK
    )

@router.post("/", response_model=SuccessResponse)
def create_grafana_source(
    grafana_source_in: GrafanaSourceCreate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("create_grafana_source")),
):
    """
    Create a new Grafana source.

    Source URL should start with http:// or https:// and remove trailing slash if present.
    """
    # Ensure the URL starts with http:// or https:// and remove trailing slash if present
    grafana_source_in.source_url = format_source_url(grafana_source_in.source_url)

    # 1. Ensure the linked DataSource exists
    data_source = db.get(DataSource, grafana_source_in.data_source_id)
    if not data_source:
        return ResponseController.send_error(
            error="Associated DataSource not found",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST
        )
    
    # Also check if linked DataSource is a Grafana source
    if data_source.type != "grafana":
        return ResponseController.send_error(
            error="Associated DataSource is not a Grafana source",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST
        )

    # 2. Create the new Grafana source
    grafana_source = GrafanaSource(
        data_source_id=grafana_source_in.data_source_id,
        source_url=grafana_source_in.source_url,
        auth_type=grafana_source_in.auth_type,
        auth_username=grafana_source_in.auth_username,
        auth_password=grafana_source_in.auth_password,
        bearer_token=grafana_source_in.bearer_token,
    )
    db.add(grafana_source)
    db.commit()
    db.refresh(grafana_source)

    # 3. Build the response
    pydantic_grafana_source = GrafanaSourceRead.model_validate(grafana_source)
    result = {"grafana_source": pydantic_grafana_source}

    return ResponseController.send_response(
        result=result,
        message="Grafana source created successfully",
        code=status.HTTP_201_CREATED
    )


@router.put("/{grafana_source_id}", response_model=SuccessResponse)
def update_grafana_source(
    grafana_source_id: int,
    grafana_source_in: GrafanaSourceUpdate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("update_grafana_source")),
):
    """Update a Grafana source by ID."""
    grafana_source = db.get(GrafanaSource, grafana_source_id)
    if not grafana_source:
        return ResponseController.send_error(
            error="Grafana source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )
    
    # Ensure the linked DataSource exists
    if grafana_source_in.data_source_id is not None:
        data_source = db.get(DataSource, grafana_source_in.data_source_id)
        if not data_source:
            return ResponseController.send_error(
                error="Associated DataSource not found",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST
            )
        
        # Also check if linked DataSource is a Grafana source
        if data_source.type != "grafana":
            return ResponseController.send_error(
                error="Associated DataSource is not a Grafana source",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST
            )
    
    # Handle auth_type change
    if grafana_source_in.auth_type is not None and grafana_source_in.auth_type != grafana_source.auth_type:
        if grafana_source.auth_type == "basic" and grafana_source_in.auth_type == "bearer":
            # Switching from basic to bearer, remove username and password
            grafana_source.auth_username = None
            grafana_source.auth_password = None
        elif grafana_source.auth_type == "bearer" and grafana_source_in.auth_type == "basic":
            # Switching from bearer to basic, remove bearer token
            grafana_source.bearer_token = None
        grafana_source.auth_type = grafana_source_in.auth_type

    # Update fields only if provided
    if grafana_source_in.source_url is not None:
        # Ensure the URL starts with http:// or https:// and remove trailing slash if present
        grafana_source_in.source_url = format_source_url(grafana_source_in.source_url)
        grafana_source.source_url = grafana_source_in.source_url

    if grafana_source_in.auth_type is not None:
        grafana_source.auth_type = grafana_source_in.auth_type

    if grafana_source_in.auth_username is not None:
        grafana_source.auth_username = grafana_source_in.auth_username

    if grafana_source_in.auth_password is not None:
        grafana_source.auth_password = grafana_source_in.auth_password

    if grafana_source_in.bearer_token is not None:
        grafana_source.bearer_token = grafana_source_in.bearer_token
    
    if grafana_source_in.data_source_id is not None:
        grafana_source.data_source_id = grafana_source_in.data_source_id

    grafana_source.updated_at = datetime.now(UTC)
    db.add(grafana_source)
    db.commit()
    db.refresh(grafana_source)

    pydantic_grafana_source = GrafanaSourceRead.model_validate(grafana_source)
    result = {"grafana_source": pydantic_grafana_source}

    return ResponseController.send_response(
        result=result,
        message="Grafana source updated successfully",
        code=status.HTTP_200_OK,
    )


@router.delete("/{grafana_source_id}", response_model=SuccessResponse)
def delete_grafana_source(
    grafana_source_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("delete_grafana_source")),
):
    """Delete a Grafana source by ID."""
    grafana_source = db.get(GrafanaSource, grafana_source_id)
    if not grafana_source:
        return ResponseController.send_error(
            error="Grafana source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    db.delete(grafana_source)
    db.commit()

    return ResponseController.send_response(
        result={},
        message="Grafana source deleted successfully",
        code=status.HTTP_200_OK
    )
