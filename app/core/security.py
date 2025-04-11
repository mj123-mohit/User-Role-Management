from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import jwt
from app.core.config import settings
from fastapi import status
from app.core.response_controller import ResponseController

BLACKLIST = set()


def create_access_token(username: str, 
                     expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with an expiration."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(username),
        "exp": expire
    }
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> str:
    """Decodes & validates the JWT; returns the username if valid."""
    if not token:
        return ResponseController.send_error(
            error="Token is missing", 
            error_messages={}, 
            code=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return ResponseController.send_error(
                error="Token payload is invalid: missing 'sub'.", 
                error_messages={}, 
                code=status.HTTP_401_UNAUTHORIZED)
        # Check if token is blacklisted
        if token in BLACKLIST:
            return ResponseController.send_error(
                error="Token has been revoked.", 
                error_messages={}, 
                code=status.HTTP_401_UNAUTHORIZED)
        return username
    except jwt.ExpiredSignatureError:
        return ResponseController.send_error(
            error="Token has expired.", 
            error_messages={}, 
            code=status.HTTP_401_UNAUTHORIZED)
    except jwt.JWTError:
        return ResponseController.send_error(
            error="Could not validate token.", 
            error_messages={}, 
            code=status.HTTP_401_UNAUTHORIZED)

