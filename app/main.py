import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware


from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.api.routes.html import router as html_router
from app.core.config import Settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.core.settings import get_settings


def get_application(settings: Settings = get_settings()) -> FastAPI:
    application = FastAPI(
        title=settings.app_name, debug=settings.debug, version=settings.version
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.add_exception_handler(ValidationError, http422_error_handler)

    application.include_router(html_router)
    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)  # nosec
