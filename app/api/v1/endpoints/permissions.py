# app/api/v1/endpoints/permissions.py

from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.api.deps import get_db_session, user_has_permission
from app.models.permission import Permission
from app.schemas.permission import PermissionRead

router = APIRouter()

@router.get("/", response_model=List[PermissionRead])
def read_permissions(
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_permission")),
):
    """List all permissions."""
    permissions = db.exec(select(Permission)).all()
    return permissions

