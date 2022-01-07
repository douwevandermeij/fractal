import json
import uuid
from abc import ABC, abstractmethod
from calendar import timegm
from datetime import datetime
from typing import Dict

from jose import ExpiredSignatureError, JWTError, jwt

from fractal.contrib.tokens.exceptions import (
    TokenExpiredException,
    TokenInvalidException,
)
from fractal.contrib.tokens.settings import (
    ACCESS_TOKEN_EXPIRATION_SECONDS,
    REFRESH_TOKEN_EXPIRATION_SECONDS,
)
from fractal.core.services import Service
from fractal.core.utils.application_context import ApplicationContext


class TokenService(Service):
    @abstractmethod
    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        raise NotImplementedError

    def _prepare(
        self, payload: Dict, token_type: str, seconds_valid: int, issuer: str
    ) -> Dict:
        utcnow = timegm(datetime.utcnow().utctimetuple())
        if not seconds_valid:
            seconds_valid = (
                REFRESH_TOKEN_EXPIRATION_SECONDS
                if token_type == "refresh"
                else ACCESS_TOKEN_EXPIRATION_SECONDS
            )
        payload.update(
            {
                "iat": utcnow,
                "nbf": utcnow,
                "jti": str(uuid.uuid4()),
                "iss": issuer,
                "exp": utcnow + seconds_valid,
                "typ": token_type,
            }
        )
        return payload

    @abstractmethod
    def verify(self, token: str, *, typ: str):
        raise NotImplementedError


class DummyJsonTokenService(TokenService):
    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return json.dumps(payload)

    def verify(self, token: str, *, typ: str):
        try:
            return json.loads(token)
        except Exception:
            raise TokenInvalidException()


class DummyTokenService(TokenService):
    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return json.dumps(payload)

    def verify(self, token: str, *, typ: str):
        return dict(
            iss="dummy",
            sub=str(uuid.uuid4()),
            account=str(uuid.uuid4()),
            email="dummy@dummy.dummy",
            typ=typ,
        )


class StaticTokenService(TokenService):
    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return json.dumps(payload)

    def verify(self, token: str, *, typ: str):
        return dict(
            iss="dummy",
            sub="00000000-0000-0000-0000-000000000000",
            account="00000000-0000-0000-0000-000000000000",
            email="dummy@dummy.dummy",
            typ=typ,
            roles=["user", "admin"],
        )


class JwtTokenService(TokenService, ABC):
    @abstractmethod
    def decode(self, token: str):
        raise NotImplementedError

    def verify(self, token: str, *, typ: str):
        try:
            payload = self.decode(token)
        except ExpiredSignatureError:
            raise TokenExpiredException()
        except JWTError:
            raise TokenInvalidException()
        if payload["typ"] != typ:
            raise TokenInvalidException()
        return payload


class SymmetricJwtTokenService(JwtTokenService):
    def __init__(self, issuer: str, secret: str):
        self.issuer = issuer
        self.secret = secret
        self.algorithm = "HS256"

    @classmethod
    def install(cls, context: ApplicationContext):
        app_name, app_env, app_domain, secret_key = context.get_parameters(
            ["app_name", "app_env", "app_domain", "secret_key"]
        )
        yield cls(
            f"{app_name}@{app_env}.{app_domain}",
            secret_key,
        )

    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return jwt.encode(
            self._prepare(payload, token_type, seconds_valid, self.issuer),
            self.secret,
            algorithm=self.algorithm,
        )

    def decode(self, token: str):
        return jwt.decode(token, self.secret, algorithms=self.algorithm)


class AsymmetricJwtTokenService(JwtTokenService):
    def __init__(self, issuer: str, private_key: str, public_key: str):
        self.issuer = issuer
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = "RS256"

    @classmethod
    def install(cls, context: ApplicationContext):
        app_name, app_env, app_domain, private_key, public_key = context.get_parameters(
            ["app_name", "app_env", "app_domain", "private_key", "public_key"]
        )
        yield cls(
            f"{app_name}@{app_env}.{app_domain}",
            private_key,
            public_key,
        )

    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return jwt.encode(
            self._prepare(payload, token_type, seconds_valid, self.issuer),
            self.private_key,
            algorithm=self.algorithm,
        )

    def decode(self, token: str):
        return jwt.decode(token, self.public_key, algorithms=self.algorithm)
