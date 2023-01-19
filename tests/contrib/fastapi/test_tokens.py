def test_get_payload(token_roles_service_fractal, token):
    from fractal.contrib.fastapi.routers.tokens import get_payload

    inner = get_payload(token_roles_service_fractal)
    inner(token)


def test_get_payload_roles(token_roles_service_fractal, admin_role_token):
    from fractal.contrib.fastapi.routers.tokens import get_payload_roles

    inner = get_payload_roles(token_roles_service_fractal, endpoint="test")
    inner(admin_role_token)
