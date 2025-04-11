from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
# from contextlib import asynccontextmanager
from app.api.v1.api_v1 import api_router
from app.core.config import settings
# from app.db.database import engine
# from app.db.base import Base
# from app.core.init_db import seed_db
from fastapi.middleware.cors import CORSMiddleware
from app.core.response_controller import ResponseController

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # **Startup Tasks**
#     Base.metadata.create_all(engine)
#     seed_db()
#     # If you have asynchronous startup tasks, perform them here
#     yield
#     # **Shutdown Tasks**
#     # Perform any cleanup if necessary

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        # lifespan=lifespan
    )
    # https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
    origins = [
        "https://anveshan.allgetz.com",
        "http://localhost",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware, 
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        """
        Override the default HTTPException handler to change the response format.
        """
        # If the exception detail is a dict, return it directly
        if isinstance(exc.detail, dict):
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail  # No "detail" key here
            )
        
        # Otherwise, building our own structure
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "metadata": {
                    "api_version": ResponseController._api_version
                },
                "data": {}
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Catch all Pydantic validation errors and transform them
        into your desired custom structure.
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": f"{exc.errors()[0]['msg']}",
                "metadata": {
                    "api_version": ResponseController._api_version
                },
                "data": {},
            },
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
