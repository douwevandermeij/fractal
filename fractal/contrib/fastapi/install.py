import logging

try:
    import sentry_sdk
except ImportError:
    sentry = False
else:
    sentry = True

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from fractal.contrib.fastapi.exceptions.error_message import ErrorMessage
from fractal.core.exceptions import DomainException
from fractal.core.utils.settings import Settings


def install_fastapi(settings: Settings):
    app = FastAPI(
        title=getattr(settings, "APP_NAME", "Fractal service"),
        version=getattr(settings, "APP_VERSION", "0.1.0"),
        root_path=getattr(settings, "OPENAPI_PREFIX_PATH", ""),
        openapi_url="/openapi.json"
        if str(getattr(settings, "APIDOCS_ENABLED", "true")).lower()
        in ["1", "yes", "true"]
        else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(settings, "ALLOW_ORIGINS", "").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if sentry:
        if sentry_dsn := getattr(settings, "SENTRY_DSN", ""):
            sentry_sdk.init(dsn=sentry_dsn)

    @app.exception_handler(DomainException)
    def unicorn_domain_exception_handler(request: Request, exc: DomainException):
        logger = logging.getLogger("app")
        if isinstance(exc.status_code, int) and 400 <= exc.status_code < 500:
            logger.warning(f"{exc.code} - {exc.message}")
        else:
            logger.error(f"{exc.code} - {exc.message}")

        if sentry:
            sentry_sdk.capture_exception(exc)

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorMessage(
                code=exc.code,
                message=exc.message,
            ).dict(),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    def unicorn_exception_handler(request: Request, exc: Exception):
        logging.error(exc)

        if sentry:
            sentry_sdk.capture_exception(exc)

        return JSONResponse(
            status_code=500,
            content=ErrorMessage(
                code=exc.__class__.__name__,
                message=str(exc),
            ).dict(),
        )

    return app
