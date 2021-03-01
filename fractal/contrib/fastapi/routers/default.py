from fastapi import APIRouter

from fractal.contrib.fastapi.routers import Routes
from fractal.contrib.fastapi.routers.domain.models import AdapterInfo, Info
from fractal.core.utils.application_context import ApplicationContext


def inject_default_routes(context: ApplicationContext):
    router = APIRouter()

    @router.get(Routes.ROOT)
    def read_root():
        return {"FastAPI": "Example"}

    @router.get(Routes.INFO, responses={200: {"model": Info}})
    def info():
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
        return data

    @router.get(Routes.HEALTHZ)
    def healthz():
        return "ok"

    return router
