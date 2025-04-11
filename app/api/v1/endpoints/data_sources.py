# app/api/v1/endpoints/data_sources.py

from fastapi import APIRouter, Depends, status
from sqlalchemy import and_
from sqlmodel import Session, select
from datetime import datetime, UTC

from app.api.deps import get_db_session, user_has_permission, get_current_user
from app.schemas.user import UserPermissions
from app.models.data_source import DataSource
from app.models.grafana_source import GrafanaSource
from app.models.kibana_source import KibanaSource

from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceRead,
    DataSourceUpdate,
)
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse

router = APIRouter()

@router.get("/", response_model=SuccessResponse)
def read_data_sources(
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_data_source")),
):
    """List all data sources."""
    data_sources = db.exec(select(DataSource)).all()

    # Ensure grafana or kibana sources are loaded for each data source
    for data_source in data_sources:
        if data_source.type == "grafana":
            data_source.grafana_sources = db.exec(
                select(GrafanaSource).where(GrafanaSource.data_source_id == data_source.id)
            ).all()
        elif data_source.type == "kibana":
            data_source.kibana_sources = db.exec(
                select(KibanaSource).where(KibanaSource.data_source_id == data_source.id)
            ).all()

    pydantic_data_sources = [DataSourceRead.model_validate(ds) for ds in data_sources]

    result = {"data_sources": pydantic_data_sources}
    return ResponseController.send_response(
        result=result,
        message="List of data sources",
        code=status.HTTP_200_OK
    )

@router.get("/{data_source_id}", response_model=SuccessResponse)
def read_data_source(
    data_source_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_data_source")),
):
    """Retrieve a single data source by its ID."""
    data_source = db.get(DataSource, data_source_id)
    if not data_source:
        return ResponseController.send_error(
            error="Data source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    pydantic_data_source = DataSourceRead.model_validate(data_source)
    result = {"data_source": pydantic_data_source}

    return ResponseController.send_response(
        result=result,
        message="Data source details",
        code=status.HTTP_200_OK
    )

@router.post("/", response_model=SuccessResponse)
def create_data_source(
    data_source_in: DataSourceCreate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("create_data_source")),
    current_user: UserPermissions = Depends(get_current_user),
):
    """Create a new data source."""
    existing_data_source = db.exec(
        select(DataSource).where(DataSource.name == data_source_in.name)
    ).first()
    if existing_data_source:
        return ResponseController.send_error(
            error="Data source name already in use",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST
        )

    data_source = DataSource(
        type=data_source_in.type,
        name=data_source_in.name,
        description=data_source_in.description,
        status=data_source_in.status,
        created_by_id=current_user.id
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    pydantic_data_source = DataSourceRead.model_validate(data_source)
    result = {"data_source": pydantic_data_source}

    return ResponseController.send_response(
        result=result,
        message="Data source created successfully",
        code=status.HTTP_201_CREATED
    )

@router.put("/{data_source_id}", response_model=SuccessResponse)
def update_data_source(
    data_source_id: int,
    data_source_in: DataSourceUpdate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("update_data_source")),
):
    """Update an existing data source by ID."""
    data_source = db.get(DataSource, data_source_id)
    if not data_source:
        return ResponseController.send_error(
            error="Data source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    # Check if new name is already in use by another data source
    if data_source_in.name is not None:
        existing_data_source = db.exec(
            select(DataSource)
            .where(and_(DataSource.name == data_source_in.name, DataSource.id != data_source_id))
        ).first()
        if existing_data_source:
            return ResponseController.send_error(
                error="Data source name already in use",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST
            )
        data_source.name = data_source_in.name

    if data_source_in.type is not None:
        data_source.type = data_source_in.type

    if data_source_in.description is not None:
        data_source.description = data_source_in.description

    if data_source_in.status is not None:
        data_source.status = data_source_in.status

    data_source.updated_at = datetime.now(UTC)
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    pydantic_data_source = DataSourceRead.model_validate(data_source)
    result = {"data_source": pydantic_data_source}

    return ResponseController.send_response(
        result=result,
        message="Data source updated successfully",
        code=status.HTTP_200_OK
    )

@router.delete("/{data_source_id}", response_model=SuccessResponse)
def delete_data_source(
    data_source_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("delete_data_source")),
):
    """Delete a data source by ID."""
    data_source = db.get(DataSource, data_source_id)
    if not data_source:
        return ResponseController.send_error(
            error="Data source not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND
        )

    db.delete(data_source)
    db.commit()

    return ResponseController.send_response(
        result={},
        message="Data source deleted successfully",
        code=status.HTTP_200_OK
    )
