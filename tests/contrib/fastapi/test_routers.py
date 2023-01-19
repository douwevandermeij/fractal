import json


def test_default_routes_root(fastapi_client, settings):
    from fractal.contrib.fastapi.routers import Routes

    response = fastapi_client.get(Routes.ROOT)
    assert response.status_code == 200
    assert json.loads(response.content) == {"FastAPI": settings.APP_NAME}


def test_default_routes_info(fastapi_client, token):
    from fractal.contrib.fastapi.routers import Routes

    response = fastapi_client.get(
        Routes.INFO, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert {(i["adapter"], i["status_ok"]) for i in json.loads(response.content)} == {
        ("InMemoryRepository", True),
        ("FakeService", True),
        # ("FractalDummyJsonTokenService", True),
        # ("DummyRolesService", True),
    }


def test_default_routes_info_token_error(failing_service_fastapi_client):
    from fractal.contrib.fastapi.routers import Routes

    response = failing_service_fastapi_client.get(Routes.INFO)
    assert response.status_code == 401


def test_default_routes_info_error(failing_service_fastapi_client, token):
    from fractal.contrib.fastapi.routers import Routes

    response = failing_service_fastapi_client.get(
        Routes.INFO, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert {(i["adapter"], i["status_ok"]) for i in json.loads(response.content)} == {
        # ("DummyRolesService", True),
        ("InMemoryRepository", True),
        ("FakeService", True),
        ("FailingService", False),
        # ("FractalDummyJsonTokenService", True),
    }


def test_not_existing_route(failing_route_fastapi_client):
    from fractal.contrib.fastapi.routers import Routes

    response = failing_route_fastapi_client.get(Routes.INFO)
    assert response.status_code == 404


def test_failing_route(failing_route_fastapi_client):
    from fractal.contrib.fastapi.routers import Routes

    response = failing_route_fastapi_client.get(Routes.ROOT)
    assert response.status_code == 500
    assert json.loads(response.content) == {
        "code": "FAILING_ROUTE",
        "message": "failing_route",
    }
