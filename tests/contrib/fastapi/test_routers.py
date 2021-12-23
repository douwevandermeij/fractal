import json


def test_default_routes_root(fastapi_client):
    from fractal.contrib.fastapi.routers import Routes

    response = fastapi_client.get(Routes.ROOT)
    assert response.status_code == 200
    assert json.loads(response.content) == {"FastAPI": "Fractal Service"}


def test_default_routes_info(fastapi_client, token):
    from fractal.contrib.fastapi.routers import Routes

    response = fastapi_client.get(Routes.INFO, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"adapter": "InMemoryRepository", "status_ok": True},
        {"adapter": "FakeService", "status_ok": True},
    ]


def test_default_routes_info_token_error(failing_service_fastapi_client):
    from fractal.contrib.fastapi.routers import Routes

    response = failing_service_fastapi_client.get(Routes.INFO)
    assert response.status_code == 401


def test_default_routes_info_error(failing_service_fastapi_client, token):
    from fractal.contrib.fastapi.routers import Routes

    response = failing_service_fastapi_client.get(Routes.INFO, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"adapter": "InMemoryRepository", "status_ok": True},
        {"adapter": "FakeService", "status_ok": True},
        {"adapter": "FailingService", "status_ok": False},
    ]


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
