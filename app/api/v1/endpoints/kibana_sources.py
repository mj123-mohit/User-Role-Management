# app/api/v1/endpoints/kibana_sources.py

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from datetime import datetime, UTC

from app.api.deps import get_db_session, format_source_url, user_has_permission
from app.schemas.kibana_source import (
    KibanaSourceCreate,
    KibanaSourceRead,
    KibanaSourceUpdate,
)
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse
from app.models.kibana_source import KibanaSource
from app.models.data_source import DataSource

router = APIRouter()

@router.get("/", response_model=SuccessResponse)
def read_kibana_sources(
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_kibana_source")),
):
    """List all Kibana sources."""
    kibana_sources = db.exec(select(KibanaSource)).all()
    pydantic_kibana_sources = [
        KibanaSourceRead.model_validate(ks) for ks in kibana_sources
    ]

    result = {"kibana_sources": pydantic_kibana_sources}
    return ResponseController.send_response(
        result=result,
        message="List of Kibana sources",
        code=status.HTTP_200_OK
    )

@router.get("/{kibana_source_id}", response_model=SuccessResponse)
def read_kibana_source(
    kibana_source_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_kibana_source")),
):
    """Retrieve a single Kibana source by its ID."""
    kibana_source = db.get(KibanaSource, kibana_source_id)
    if not kibana_source:
        return ResponseController.send_error(
            error="Kibana source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    pydantic_kibana_source = KibanaSourceRead.model_validate(kibana_source)
    result = {"kibana_source": pydantic_kibana_source}

    return ResponseController.send_response(
        result=result,
        message="Kibana source details",
        code=status.HTTP_200_OK
    )

@router.post("/", response_model=SuccessResponse)
def create_kibana_source(
    kibana_source_in: KibanaSourceCreate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("create_kibana_source")),
):
    """
    Create a new Kibana source.

    Source URL should start with http:// or https:// and remove trailing slash if present.
    """
    # Ensure the URL starts with http:// or https:// and remove trailing slash if present
    kibana_source_in.source_url = format_source_url(kibana_source_in.source_url)

    # 1. Ensure the linked DataSource exists
    data_source = db.get(DataSource, kibana_source_in.data_source_id)
    if not data_source:
        return ResponseController.send_error(
            error="Associated DataSource not found",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST
        )
    
    # Also check if linked DataSource is a Kibana source
    if data_source.type != "kibana":
        return ResponseController.send_error(
            error="Associated DataSource is not a Kibana source",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST
        )

    # 2. Create the new Kibana source
    kibana_source = KibanaSource(
        data_source_id=kibana_source_in.data_source_id,
        source_url=kibana_source_in.source_url,
        auth_type=kibana_source_in.auth_type,
        auth_username=kibana_source_in.auth_username,
        auth_password=kibana_source_in.auth_password,
        bearer_token=kibana_source_in.bearer_token,
    )
    db.add(kibana_source)
    db.commit()
    db.refresh(kibana_source)

    # 3. Build the response
    pydantic_kibana_source = KibanaSourceRead.model_validate(kibana_source)
    result = {"kibana_source": pydantic_kibana_source}

    return ResponseController.send_response(
        result=result,
        message="Kibana source created successfully",
        code=status.HTTP_201_CREATED
    )


@router.put("/{kibana_source_id}", response_model=SuccessResponse)
def update_kibana_source(
    kibana_source_id: int,
    kibana_source_in: KibanaSourceUpdate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("update_kibana_source")),
):
    """Update a Kibana source by ID."""
    kibana_source = db.get(KibanaSource, kibana_source_id)
    if not kibana_source:
        return ResponseController.send_error(
            error="Kibana source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )
    
    # Ensure the linked DataSource exists
    if kibana_source_in.data_source_id is not None:
        data_source = db.get(DataSource, kibana_source_in.data_source_id)
        if not data_source:
            return ResponseController.send_error(
                error="Associated DataSource not found",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST
            )
        
        # Also check if linked DataSource is a Kibana source
        if data_source.type != "kibana":
            return ResponseController.send_error(
                error="Associated DataSource is not a Kibana source",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST
            )
    
    # Handle auth_type change
    if kibana_source_in.auth_type is not None and kibana_source_in.auth_type != kibana_source.auth_type:
        if kibana_source.auth_type == "basic" and kibana_source_in.auth_type == "bearer":
            # Switching from basic to bearer, remove username and password
            kibana_source.auth_username = None
            kibana_source.auth_password = None
        elif kibana_source.auth_type == "bearer" and kibana_source_in.auth_type == "basic":
            # Switching from bearer to basic, remove bearer token
            kibana_source.bearer_token = None
        kibana_source.auth_type = kibana_source_in.auth_type

    # Update fields only if provided
    if kibana_source_in.source_url is not None:
        # Ensure the URL starts with http:// or https:// and remove trailing slash if present
        kibana_source_in.source_url = format_source_url(kibana_source_in.source_url)
        kibana_source.source_url = kibana_source_in.source_url

    if kibana_source_in.auth_type is not None:
        kibana_source.auth_type = kibana_source_in.auth_type

    if kibana_source_in.auth_username is not None:
        kibana_source.auth_username = kibana_source_in.auth_username

    if kibana_source_in.auth_password is not None:
        kibana_source.auth_password = kibana_source_in.auth_password

    if kibana_source_in.bearer_token is not None:
        kibana_source.bearer_token = kibana_source_in.bearer_token
    
    if kibana_source_in.data_source_id is not None:
        kibana_source.data_source_id = kibana_source_in.data_source_id

    kibana_source.updated_at = datetime.now(UTC)
    db.add(kibana_source)
    db.commit()
    db.refresh(kibana_source)

    pydantic_kibana_source = KibanaSourceRead.model_validate(kibana_source)
    result = {"kibana_source": pydantic_kibana_source}

    return ResponseController.send_response(
        result=result,
        message="Kibana source updated successfully",
        code=status.HTTP_200_OK,
    )


@router.delete("/{kibana_source_id}", response_model=SuccessResponse)
def delete_kibana_source(
    kibana_source_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("delete_kibana_source")),
):
    """Delete a Kibana source by ID."""
    kibana_source = db.get(KibanaSource, kibana_source_id)
    if not kibana_source:
        return ResponseController.send_error(
            error="Kibana source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    db.delete(kibana_source)
    db.commit()

    return ResponseController.send_response(
        result={},
        message="Kibana source deleted successfully",
        code=status.HTTP_200_OK
    )
