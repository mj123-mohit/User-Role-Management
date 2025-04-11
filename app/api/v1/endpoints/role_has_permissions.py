from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_has_permissions import RoleHasPermissions
from app.schemas.role import RoleRead
from app.api.deps import get_db_session, user_has_permission
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse
from app.schemas.role_has_permissions import AssignPermissionsRequest

router = APIRouter()

@router.post("/{role_id}/assign-permissions", response_model=SuccessResponse)
def assign_permissions_to_role(
    role_id: int,
    request: AssignPermissionsRequest,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("assign_permissions")),
):
    """Assign permissions to a role."""
    # Fetch the role by ID
    role = db.get(Role, role_id)
    if not role:
        return ResponseController.send_error(
            error="Role not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )

    # Validate the provided permission IDs
    permissions = db.exec(
        select(Permission).where(Permission.id.in_(request.permission_ids))
    ).all()
    if len(permissions) != len(request.permission_ids):
        return ResponseController.send_error(
            error="One or more permissions do not exist",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST,
        )

    # Assign the permissions
    for permission in permissions:
        existing_link = db.exec(
            select(RoleHasPermissions).where(
                RoleHasPermissions.role_id == role_id,
                RoleHasPermissions.permission_id == permission.id,
            )
        ).first()
        if not existing_link:
            role_permission = RoleHasPermissions(role_id=role_id, permission_id=permission.id)
            db.add(role_permission)

    db.commit()

    # Refresh role's permissions
    role.permissions = db.exec(
        select(Permission).join(RoleHasPermissions).where(RoleHasPermissions.role_id == role_id)
    ).all()

    # Prepare the response
    pydantic_role = RoleRead.model_validate(role)
    result = {"role": pydantic_role}

    return ResponseController.send_response(
        result=result,
        message="Permissions assigned successfully",
        code=status.HTTP_200_OK,
    )


@router.post("/{role_id}/remove-permissions", response_model=SuccessResponse)
def remove_permissions_from_role(
    role_id: int,
    request: AssignPermissionsRequest,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("remove_permissions")),
):
    """Remove permissions from a role."""
    # Fetch the role by ID
    role = db.get(Role, role_id)
    if not role:
        return ResponseController.send_error(
            error="Role not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )

    # Validate the provided permission IDs
    permissions = db.exec(
        select(Permission).where(Permission.id.in_(request.permission_ids))
    ).all()
    if len(permissions) != len(request.permission_ids):
        return ResponseController.send_error(
            error="One or more permissions do not exist",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST,
        )

    # Remove the permissions
    for permission in permissions:
        existing_link = db.exec(
            select(RoleHasPermissions).where(
                RoleHasPermissions.role_id == role_id,
                RoleHasPermissions.permission_id == permission.id,
            )
        ).first()
        if existing_link:
            db.delete(existing_link)

    db.commit()

    return ResponseController.send_response(
        result={},
        message="Permissions removed successfully",
        code=status.HTTP_200_OK,
    )
