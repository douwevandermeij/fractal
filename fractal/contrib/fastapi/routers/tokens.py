from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from fractal import Fractal
from fractal.contrib.tokens.models import TokenPayload, TokenPayloadRoles

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_payload(fractal: Fractal, *, typ: str = "access"):
    assert hasattr(fractal, "context")
    context = getattr(fractal, "context")
    assert hasattr(context, "token_service")

    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
        return TokenPayload(**context.token_service.verify(token, typ=typ))

    return _get_payload


def get_payload_roles(
    fractal: Fractal, *, endpoint: str = "", method: str = "get", typ: str = "access"
):
    assert hasattr(fractal, "context")
    context = getattr(fractal, "context")
    assert hasattr(context, "token_service")
    assert hasattr(context, "roles_service")

    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayloadRoles:
        payload = TokenPayloadRoles(**context.token_service.verify(token, typ=typ))
        payload = context.roles_service.verify(payload, endpoint, method)
        return payload

    return _get_payload
