import logging

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from fractal.contrib.fastapi.exceptions.error_message import ErrorMessage
from fractal.core.exceptions import DomainException
from fractal.core.utils.settings import Settings


def install_fastapi(settings: Settings):
    app = FastAPI(root_path=settings.OPENAPI_PREFIX_PATH)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    sentry_sdk.init(dsn=settings.SENTRY_DSN)
    app.add_middleware(
        SentryAsgiMiddleware,
    )

    @app.exception_handler(DomainException)
    def unicorn_exception_handler(request: Request, exc: DomainException):
        logger = logging.getLogger("app")
        if isinstance(exc.status_code, int) and 400 <= exc.status_code < 500:
            logger.warning(f"{exc.code} - {exc.message}")
        else:
            logger.error(f"{exc.code} - {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorMessage(
                code=exc.code,
                message=exc.message,
            ).dict(),
            headers=exc.headers,
        )

    return app
