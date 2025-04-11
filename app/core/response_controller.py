from fastapi.responses import JSONResponse
from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
import logging
from typing import Any, Dict

class ResponseController:
    # Constants
    SOMETHING_WENT_WRONG = "Something went wrong."
    ERROR_MESSAGE_ERROR = "Error"
    VALIDATION_ERROR_MESSAGE = "Validation errors"

    _api_version = "1.0"

    @classmethod
    def get_api_version(cls) -> str:
        return cls._api_version

    @staticmethod
    def send_response(result: Any, message: str, code: int = status.HTTP_200_OK) -> JSONResponse:
        """
        Success response method.
        :param result: The data to return
        :param message: The success message
        :param code: HTTP status code
        :return: A FastAPI JSONResponse
        """
        encoded_result = jsonable_encoder(result)

        response_content = {
            "success": True,
            "data": encoded_result,
            "message": message,
            "metadata": {
                "api_version": ResponseController.get_api_version(),
            },
        }
        return JSONResponse(status_code=code, content=response_content)

    @staticmethod
    def send_error(
        error: str = None,
        error_messages: Dict[str, Any] = None,
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        exc: Exception = None,
    ) -> None:
        """
        Error response method that raises an HTTPException instead of returning a response.
        :param error: Short error message
        :param error_messages: Detailed error messages
        :param code: HTTP status code
        :param exc: Exception instance (if any) for logging
        :raises: HTTPException
        """
        if exc:
            # Log the error and stacktrace
            logging.error("An exception occurred: %s", str(exc), exc_info=True)

        if not error:
            error = ResponseController.SOMETHING_WENT_WRONG

        # Construct the error response
        error_response = {
            "success": False,
            "message": error,
            "metadata": {
                "api_version": ResponseController.get_api_version(),
            },
            "data": error_messages or {},
        }

        # Raise the exception with the error response
        raise HTTPException(status_code=code, detail=error_response)
