#app.api.v1.endpoints.auth.py

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import UTC, datetime, timedelta
from app.models.user import User
from app.core.security import create_access_token 
from app.core.hashing import verify_password
from app.core.config import settings
from app.api.deps import get_session
from starlette import status
from app.core.response_controller import ResponseController
from app.schemas.response_controller import SuccessResponse
from app.schemas.login import LoginRequest
 
router = APIRouter()
 
@router.post("/login", response_model=SuccessResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_session)
):
    """Login user."""
    # Extract email and password from the request
    email = request.email
    password = request.password

    if not email:
        return ResponseController.send_error(
            error="Email field is required", 
            error_messages={}, 
            code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Fetch user from the database
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password):
        return ResponseController.send_error(
            error="Incorrect email or password", 
            error_messages={}, 
            code=status.HTTP_401_UNAUTHORIZED)
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(username=user.email, expires_delta=access_token_expires)
    
    return ResponseController.send_response(
            result={
                "access_token": {"token_type": "bearer", 
                                 "token": access_token, 
                                 "expires_at": str(datetime.now(UTC) + access_token_expires)}, 
                "user":{"email":user.email}},
            message="Login successful",
            code=status.HTTP_200_OK
        )
