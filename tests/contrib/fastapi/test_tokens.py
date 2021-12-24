def test_get_payload(dummy_token_service_fractal, token):
    from fractal.contrib.fastapi.routers.tokens import get_payload

    inner = get_payload(dummy_token_service_fractal)
    inner(token)


def test_get_payload_roles(dummy_token_service_fractal, admin_role_token):
    from fractal.contrib.fastapi.routers.tokens import get_payload_roles

    inner = get_payload_roles(dummy_token_service_fractal, roles=["admin"])
    inner(admin_role_token)
