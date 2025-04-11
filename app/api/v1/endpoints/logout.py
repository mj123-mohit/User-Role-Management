from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.response_controller import SuccessResponse
from app.core.security import BLACKLIST, decode_token
from app.api.deps import bearer_scheme
from app.core.response_controller import ResponseController

 
router = APIRouter()

# Dependency to Get Token
def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """Extracts the token string from the authorization header"""
    return credentials.credentials
 
@router.post("/", response_model=SuccessResponse)
def logout(
    token: str = Depends(get_current_token)     # Gets the actual token string
):
    """Logout user."""
    username: str = decode_token(token)     # Validate and Decode the token
    BLACKLIST.add(token)
    return ResponseController.send_response(
            result={},
            message="Logout successful",
            code=status.HTTP_200_OK
        )
