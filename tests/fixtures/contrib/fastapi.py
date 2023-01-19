import pytest


@pytest.fixture
def fastapi_client(fastapi_app_with_default_routes):
    from starlette.testclient import TestClient

    return TestClient(fastapi_app_with_default_routes)


@pytest.fixture
def a_base_model_object():
    from pydantic import BaseModel

    class ABaseModelObject(BaseModel):
        id: str
        name: str = "default_name"

    return ABaseModelObject(id="1")


@pytest.fixture
def fastapi_app(settings):
    from fractal.contrib.fastapi.install import install_fastapi

    return install_fastapi(settings)


@pytest.fixture
def fastapi_app_with_default_routes(fastapi_app, token_roles_service_fractal):
    from fractal.contrib.fastapi.routers.default import inject_default_routes

    fastapi_app.include_router(
        inject_default_routes(token_roles_service_fractal),
        tags=["default"],
    )
    return fastapi_app


@pytest.fixture
def failing_service_class():
    from fractal.core.services import Service

    class FailingService(Service):
        def is_healthy(self) -> bool:
            raise NotImplementedError

    return FailingService


@pytest.fixture
def failing_service_fastapi_client(
    fastapi_app, failing_service_class, token_roles_service_fractal
):
    from starlette.testclient import TestClient

    from fractal.contrib.fastapi.routers.default import inject_default_routes

    token_roles_service_fractal.context.install_service(failing_service_class)

    fastapi_app.include_router(
        inject_default_routes(token_roles_service_fractal),
        tags=["default"],
    )

    return TestClient(fastapi_app)


@pytest.fixture
def failing_route_fastapi_client(fastapi_app):
    from fastapi import APIRouter
    from starlette.testclient import TestClient

    from fractal.contrib.fastapi.routers import Routes
    from fractal.core.exceptions import DomainException

    router = APIRouter()

    @router.get(Routes.ROOT)
    def read_root():
        raise DomainException(
            message="failing_route",
            code="FAILING_ROUTE",
            status_code=500,
        )

    fastapi_app.include_router(router, tags=["default"])

    return TestClient(fastapi_app)
