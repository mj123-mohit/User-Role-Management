# app/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, status
from sqlalchemy import and_
from sqlmodel import Session, select
from app.api.deps import get_db_session, user_has_permission
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.hashing import hash_password
from datetime import datetime, UTC
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse

router = APIRouter()

@router.get("/", response_model=SuccessResponse)
def read_users(
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_user")),
):
    """List all users."""
    users = db.exec(select(User)).all()

    # Convert each ORM user to the Pydantic model
    pydantic_users = [UserRead.model_validate(u) for u in users]

    result = {"users": pydantic_users}

    return ResponseController.send_response(
        result=result,
        message="List of users",
        code=status.HTTP_200_OK
    )

@router.get("/{user_id}", response_model=SuccessResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("read_user")),
):
    """User details."""
    user = db.get(User, user_id)
    if not user:
        return ResponseController.send_error(
            error="User not found", 
            error_messages={}, 
            code=status.HTTP_404_NOT_FOUND)
    
    pydantic_user = UserRead.model_validate(user)
    result = {"user": pydantic_user}

    return ResponseController.send_response(
        result=result,
        message="User details",
        code=status.HTTP_200_OK)


@router.post("/", response_model=SuccessResponse)
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("create_user")),
):
    """Create a new user."""
    existing_user = db.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        return ResponseController.send_error(
            error="Email already registered", 
            error_messages={}, 
            code=status.HTTP_400_BAD_REQUEST)

    user_role = db.exec(select(Role).where(Role.name == user_in.role)).first()
    if not user_role:
        return ResponseController.send_error(
            error="Role not found, please create it first", 
            error_messages={}, 
            code=status.HTTP_400_BAD_REQUEST)

    updated_user = User(
        name=user_in.name,
        email=user_in.email,
        password=hash_password(user_in.password),
        status=user_in.status,
        role=user_role, 
    )
    db.add(updated_user)
    db.commit()
    db.refresh(updated_user)
    
    pydantic_user = UserRead.model_validate(updated_user)
    result = {"user": pydantic_user}
    
    return ResponseController.send_response(
        result=result,
        message="User created successfully",
        code=status.HTTP_201_CREATED
    )

@router.delete("/{user_id}", response_model=SuccessResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("delete_user")),
):
    """Delete a user by ID."""
    user = db.get(User, user_id)
    if not user:
        return ResponseController.send_error(
            error="User not found", 
            error_messages={}, 
            code=status.HTTP_404_NOT_FOUND)

    db.delete(user)
    db.commit()
    return ResponseController.send_response(
        result={},
        message="User deleted successfully",
        code=status.HTTP_200_OK)

@router.put("/{user_id}", response_model=SuccessResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db_session),
    has_perm: bool = Depends(user_has_permission("update_user")),
):
    """Update a user by ID."""
    user = db.get(User, user_id)
    if not user:
        return ResponseController.send_error(
            error="User not found", 
            error_messages={}, 
            code=status.HTTP_404_NOT_FOUND)

    # Update name
    if user_in.name is not None:
        user.name = user_in.name

    # Update email with uniqueness check
    if user_in.email is not None:
        existing_user = db.exec(
            select(User).where(and_(User.email == user_in.email, User.id != user_id))
        ).first()
        if existing_user:
            return ResponseController.send_error(
                error="Email already in use", 
                error_messages={}, 
                code=status.HTTP_400_BAD_REQUEST)
        user.email = user_in.email

    # Update status with validation
    if user_in.status is not None:
        if user_in.status in ["active", "disabled"]:
            user.status = user_in.status
        else:
            return ResponseController.send_error(
                error="Invalid status; Can be either 'active' or 'disabled'", 
                error_messages={}, 
                code=status.HTTP_400_BAD_REQUEST)

    # Update role
    if user_in.role is not None:
        user_role = db.exec(
            select(Role).where(Role.name == user_in.role)
        ).first()
        if not user_role:
            return ResponseController.send_error(
                error="Role not found, please create it first", 
                error_messages={}, 
                code=status.HTTP_400_BAD_REQUEST)
        user.role = user_role  # Assign the Role object directly

    user.updated_at=datetime.now(UTC)

    db.add(user)
    db.commit()
    db.refresh(user)
    pydantic_user = UserRead.model_validate(user)
    result = {"user": pydantic_user}

    return ResponseController.send_response(
        result=result,
        message="User updated successfully",
        code=status.HTTP_200_OK
    )