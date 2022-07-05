import json
import uuid
from abc import ABC, abstractmethod
from calendar import timegm
from datetime import datetime
from typing import Dict
from urllib.request import urlopen

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from jose import ExpiredSignatureError, JWTError, jwt

from fractal.contrib.tokens.exceptions import (
    NotAllowedException,
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

    @abstractmethod
    def decode(self, token: str):
        raise NotImplementedError

    @abstractmethod
    def get_unverified_claims(self, token: str):
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

    def decode(self, token: str):
        return json.loads(token)

    def get_unverified_claims(self, token: str):
        return self.decode(token)


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

    def decode(self, token: str):
        return dict(
            iss="dummy",
            sub=str(uuid.uuid4()),
            account=str(uuid.uuid4()),
            email="dummy@dummy.dummy",
            typ="access",
        )

    def get_unverified_claims(self, token: str):
        return self.decode(token)


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

    def decode(self, token: str):
        return dict(
            iss="dummy",
            sub="00000000-0000-0000-0000-000000000000",
            account="00000000-0000-0000-0000-000000000000",
            email="dummy@dummy.dummy",
            typ="access",
            roles=["user", "admin"],
        )

    def get_unverified_claims(self, token: str):
        return self.decode(token)


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
        app_name, app_env, app_domain, secret_key = context.settings.get_parameters(
            ["APP_NAME", "APP_ENV", "APP_DOMAIN", "SECRET_KEY"]
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

    def get_unverified_claims(self, token: str):
        return jwt.get_unverified_claims(token)


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

    def get_unverified_claims(self, token: str):
        return jwt.get_unverified_claims(token)


class ExtendedAsymmetricJwtTokenService(AsymmetricJwtTokenService):
    def __init__(
        self, issuer: str, private_key: str, public_key: RSAPublicKey, kid: str
    ):
        super(ExtendedAsymmetricJwtTokenService, self).__init__(issuer, private_key, "")
        self.public_key = public_key
        self.kid = kid

    def decode(self, token: str):
        return jwt.decode(
            token, self.public_key, algorithms=self.algorithm, issuer=self.issuer
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
            headers={"kid": self.kid},
        )


class AutomaticJwtTokenService(JwtTokenService):
    def __init__(self, issuer: str, secret: str):
        self.issuer = issuer
        self.symmetric_token_service = SymmetricJwtTokenService(
            issuer=issuer,
            secret=secret,
        )

    @classmethod
    def install(cls, context: ApplicationContext):
        yield cls(
            context.settings.ACCOUNT_SERVICE_HOST,
            context.settings.SECRET_KEY,
        )

    def generate(
        self,
        payload: Dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return self.symmetric_token_service.generate(payload, token_type, seconds_valid)

    def verify(self, token: str, *, typ: str):
        headers = jwt.get_unverified_headers(token)
        claims = jwt.get_unverified_claims(token)
        if headers["alg"] == "HS256":
            return self.symmetric_token_service.verify(token, typ=typ)
        if headers["alg"] == "RS256":
            jsonurl = urlopen(f"{claims['iss']}/public/keys")
            jwks = json.loads(jsonurl.read())
            for key in jwks:
                if key["id"] == headers["kid"]:
                    public_key = serialization.load_pem_public_key(
                        key["public_key"].encode("utf-8"), backend=default_backend()
                    )
                    asymmetric_token_service = ExtendedAsymmetricJwtTokenService(
                        issuer=self.issuer,
                        private_key="",
                        public_key=public_key,
                        kid=key["id"],
                    )
                    return asymmetric_token_service.verify(token, typ=typ)
        raise NotAllowedException("No permission!")

    def decode(self, token: str):
        ...

    def get_unverified_claims(self, token: str):
        return jwt.get_unverified_claims(token)
