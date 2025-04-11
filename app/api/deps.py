# app/api/deps.py

from fastapi import Depends, status
from typing import Callable
from sqlmodel import Session, select
from app.core.security import decode_token
from app.db.database import get_session
from app.models.user import User
from app.schemas.user import UserPermissions
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.response_controller import ResponseController
import re

bearer_scheme = HTTPBearer()

def format_source_url(url: str) -> str:
    """Ensures the URL starts with 'http://' or 'https://', and removes trailing slash if present."""
    # Ensure the URL starts with http:// or https://
    if not re.match(r'^https?://', url):
        return ResponseController.send_error(
            error="Invalid URL format. URL must start with 'http://' or 'https://'.", 
            error_messages={}, 
            code=status.HTTP_400_BAD_REQUEST)

    # Remove trailing slash if present
    return url.rstrip('/')

def get_db_session():
    # Use get_session directly and delegate to it
    yield from get_session()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
        db: Session = Depends(get_db_session)
) -> UserPermissions:
    token = credentials.credentials
    # Decode the token to get the username
    username = decode_token(token)
    if not username:
        return ResponseController.send_error(
            error="Invalid authentication credentials.", 
            error_messages={}, 
            code=status.HTTP_401_UNAUTHORIZED)
    
    # Query the database for the user
    statement = select(User).where(User.email == username)
    user = db.exec(statement).first()
    if not user:
        return ResponseController.send_error(
            error="User not found.", 
            error_messages={}, 
            code=status.HTTP_404_NOT_FOUND)
    
    role = user.role
    permissions = set()
    for perm in role.permissions:
        permissions.add(perm.name)

    return UserPermissions(
        id=user.id,
        name=user.name,
        email=user.email,
        status=user.status,
        role=role,
        permissions=list(permissions)
    )

def user_has_permission(perm: str) -> Callable:
    def dependency(current_user: UserPermissions = Depends(get_current_user)):
        if perm not in current_user.permissions:
            return ResponseController.send_error(
                error="You don't have enough permissions.", 
                error_messages={}, 
                code=status.HTTP_403_FORBIDDEN)
        return True
    return dependency
