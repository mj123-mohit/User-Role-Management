from typing import Any
from pydantic import BaseModel
from app.core.config import settings

class Metadata(BaseModel):
    api_version: str = settings.API_V1_STR


class SuccessResponse(BaseModel):
    """
    Model for successful responses.

    Example:
    {
      "success": True,
      "data": ...,
      "message": "Data fetched successfully.",
      "metadata": {
        "api_version": "v1"
      }
    }
    """
    success: bool
    message: str
    metadata: Metadata
    data: Any


