# app/api/v1/endpoints/roles.py

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from app.api.deps import get_db_session, user_has_permission
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_has_permissions import RoleHasPermissions
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse

router = APIRouter()

@router.get("/", response_model=SuccessResponse)
def read_roles(
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_role")),
):
    """List all roles."""
    # Fetch all roles
    roles = db.exec(select(Role)).all()

    # Ensure permissions are loaded for each role
    for role in roles:
        role.permissions = db.exec(
            select(Permission).join(RoleHasPermissions).where(RoleHasPermissions.role_id == role.id)
        ).all()

    pydantic_roles = [RoleRead.model_validate(u) for u in roles]
    result = {"roles": pydantic_roles}

    return ResponseController.send_response(
        result=result,
        message="List of roles",
        code=status.HTTP_200_OK)

@router.get("/{role_id}", response_model=SuccessResponse)
def get_role(role_id: int, 
             db: Session = Depends(get_db_session),
             has_perm: bool = Depends(user_has_permission("read_role")),
             ):
    """Role details."""
    # Fetch the role by ID
    role = db.exec(select(Role).where(Role.id == role_id)).first()
    if not role:
        return ResponseController.send_error(
            error=f"Role with ID {role_id} not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )

    # Fetch related permissions
    role.permissions = db.exec(
        select(Permission).join(RoleHasPermissions).where(RoleHasPermissions.role_id == role_id)
    ).all()

    pydantic_role = RoleRead.model_validate(role)
    return ResponseController.send_response(
        result={"role": pydantic_role},
        message="Role details",
        code=status.HTTP_200_OK,
    )

@router.post("/", response_model=SuccessResponse)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("create_role")),
):
    """Create a new role with optional permissions."""
    # Check if the role name already exists
    existing_role = db.exec(select(Role).where(Role.name == role_data.name)).first()
    if existing_role:
        return ResponseController.send_error(
            error="Role with this name already exists",
            error_messages={},
            code=status.HTTP_400_BAD_REQUEST,
        )

    # Validate provided permission IDs (if any)
    permissions = []
    if role_data.permission_ids:
        permissions = db.exec(
            select(Permission).where(Permission.id.in_(role_data.permission_ids))
        ).all()
        if len(permissions) != len(role_data.permission_ids):
            return ResponseController.send_error(
                error="One or more permissions do not exist",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST,
            )

    # Create the new role
    new_role = Role(name=role_data.name)
    db.add(new_role)
    db.commit()  # Save the role to generate an ID
    db.refresh(new_role)

    # Assign permissions to the new role (if any)
    for permission in permissions:
        role_permission = RoleHasPermissions(role_id=new_role.id, permission_id=permission.id)
        db.add(role_permission)

    db.commit()  # Save role-permission relationships
    db.refresh(new_role)

    # Prepare the response
    new_role.permissions = permissions  # Attach permissions to the role object
    pydantic_new_role = RoleRead.model_validate(new_role)
    result = {"role": pydantic_new_role}

    return ResponseController.send_response(
        result=result,
        message="Role created successfully",
        code=status.HTTP_201_CREATED,
    )

@router.delete("/{role_id}", response_model=SuccessResponse)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("delete_role")),
):
    """Delete a role by ID."""
    # Fetch the role by ID
    role = db.get(Role, role_id)
    if not role:
        return ResponseController.send_error(
            error="Role not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )

    # Delete the role
    db.delete(role)
    db.commit()

    return ResponseController.send_response(
        result={},
        message="Role deleted successfully",
        code=status.HTTP_200_OK,
    )

@router.put("/{role_id}", response_model=SuccessResponse)
def rename_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("rename_role")),
):
    """Rename a role by ID."""
    role = db.get(Role, role_id)
    if not role:
        return ResponseController.send_error(
            error="Role not found",
            error_messages={},
            code=status.HTTP_404_NOT_FOUND,
        )

    if role_in.name is not None:
        # Check if name is already used
        if db.exec(select(Role).where(Role.name == role_in.name, Role.id != role_id)).first():
            return ResponseController.send_error(
                error="Role name already in use",
                error_messages={},
                code=status.HTTP_400_BAD_REQUEST,
            )
        role.name = role_in.name

    db.add(role)
    db.commit()
    db.refresh(role)

    # Fetch related permissions
    role.permissions = db.exec(
        select(Permission).join(RoleHasPermissions).where(RoleHasPermissions.role_id == role_id)
    ).all()

    pydantic_role = RoleRead.model_validate(role)
    return ResponseController.send_response(
        result={"role": pydantic_role},
        message="Role renamed successfully",
        code=status.HTTP_200_OK,
    )

