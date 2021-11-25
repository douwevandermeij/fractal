from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from fractal import Fractal
from fractal.contrib.tokens.models import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_payload(fractal: Fractal):
    assert hasattr(fractal, "context")
    context = getattr(fractal, "context")
    assert hasattr(context, "token_service")

    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
        return TokenPayload(**context.token_service.verify(token))

    return _get_payload
