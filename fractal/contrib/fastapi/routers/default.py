from typing import Optional

from fastapi import APIRouter, Depends

from fractal.contrib.fastapi.routers import Routes
from fractal.contrib.fastapi.routers.domain.models import AdapterInfo, Info
from fractal.contrib.fastapi.routers.tokens import get_payload
from fractal.contrib.tokens.fractal import DummyTokenServiceFractal
from fractal.contrib.tokens.models import TokenPayload
from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


def inject_default_routes(
    context: ApplicationContext, settings: Optional[Settings] = None
):
    router = APIRouter()

    @router.get(Routes.ROOT)
    def read_root():
        return {
            "FastAPI": settings.APP_NAME
            if settings and hasattr(settings, "APP_NAME")
            else "Fractal Service",
        }

    @router.get(Routes.INFO, responses={200: {"model": Info}})
    def info(
        payload: TokenPayload = Depends(
            get_payload(DummyTokenServiceFractal(context, settings))
        ),
    ):
        adapters = list(context.adapters())
        data = [
            AdapterInfo(
                adapter=adapter.__class__.__name__,
                status=False,
            )
            for adapter in adapters
        ]
        for i in range(len(data)):
            try:
                data[i].status_ok = adapters[i].is_healthy()
            except Exception as e:
                context.logger.error(e)
                data[i].status_ok = False
        return data

    return router
