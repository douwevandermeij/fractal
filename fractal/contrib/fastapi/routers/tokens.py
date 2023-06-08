from dataclasses import dataclass
from typing import List, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fractal_repositories.core.entity import Model
from fractal_roles.models import Role, TokenPayloadRolesMixin
from fractal_roles.services import RolesService as BaseRolesService
from fractal_tokens.services.dummy import DummyJsonTokenService
from fractal_tokens.services.generic import TokenPayload as BaseTokenPayload
from fractal_tokens.services.generic import TokenService
from fractal_tokens.services.jwt.automatic import AutomaticJwtTokenService

from fractal import ApplicationContext, Fractal
from fractal.core.services import Service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@dataclass
class TokenPayload(Model, BaseTokenPayload):
    ...


@dataclass
class TokenPayloadRoles(Model, TokenPayloadRolesMixin, BaseTokenPayload):
    roles: Optional[List[Role]] = None
    account: str = ""

    def __post_init__(self):
        if not self.roles:
            self.roles = []


class FractalAutomaticJwtTokenService(AutomaticJwtTokenService, Service):
    token_payload_cls = TokenPayloadRoles

    @classmethod
    def install(cls, context: ApplicationContext):
        yield cls(
            issuer=context.settings.JWK_SERVICE_HOST,
            secret_key=context.settings.SECRET_KEY,
            jwk_service=context.jwk_service,
        )


class FractalDummyJsonTokenService(DummyJsonTokenService, Service):
    token_payload_cls = TokenPayloadRoles

    @classmethod
    def install(cls, context: ApplicationContext):
        yield cls()


def get_payload(fractal: Fractal, *, typ: str = "access"):
    assert hasattr(fractal, "context")
    context = getattr(fractal, "context")
    assert hasattr(context, "token_service")

    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
        return context.token_service.verify(token, typ=typ)

    return _get_payload


def get_payload_roles(
    fractal: Fractal, *, endpoint: str = "", method: str = "get", typ: str = "access"
):
    assert hasattr(fractal, "context")
    context = getattr(fractal, "context")
    assert hasattr(context, "token_service")
    assert hasattr(context, "roles_service")

    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayloadRoles:
        payload = context.token_service.verify(token, typ=typ)
        payload = context.roles_service.verify(payload, endpoint, method)
        return payload

    return _get_payload


def get_token_roles_payload(
    *,
    token_service: TokenService,
    roles_service: BaseRolesService,
    endpoint: str = "",
    method: str = "get",
    typ: str = "access",
):
    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayloadRoles:
        payload = token_service.verify(token, typ=typ)
        payload = roles_service.verify(payload, endpoint, method)
        return payload

    return _get_payload
