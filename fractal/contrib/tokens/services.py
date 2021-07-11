import json
import uuid
from abc import abstractmethod
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
    def verify(self, token: str):
        raise NotImplementedError


class DummyJsonTokenService(TokenService):
    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return json.dumps(payload)

    def verify(self, token: str):
        return json.loads(token)


class SymmetricJwtTokenService(TokenService):
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

    def verify(self, token: str):
        try:
            payload = jwt.decode(token, self.secret, algorithms=self.algorithm)
        except ExpiredSignatureError:
            raise TokenExpiredException("The supplied token is expired!")
        except JWTError:
            raise TokenInvalidException("The supplied token is invalid!")
        if payload["typ"] != "access":
            raise TokenInvalidException("The supplied token is invalid!")
        return payload


class AsymmetricJwtTokenService(TokenService):
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

    def verify(self, token: str):
        try:
            payload = jwt.decode(token, self.public_key, algorithms=self.algorithm)
        except ExpiredSignatureError:
            raise TokenExpiredException("The supplied token is expired!")
        except JWTError:
            raise TokenInvalidException("The supplied token is invalid!")
        if payload["typ"] not in ["access", "refresh"]:
            raise TokenInvalidException("The supplied token is invalid!")
        return payload
