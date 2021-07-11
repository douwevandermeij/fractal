from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from fractal.core.exceptions import DomainException


class TokenInvalidException(DomainException):
    code = "TOKEN_INVALID"
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(self, message="The supplied token is invalid!", *args, **kwargs):
        super(TokenInvalidException, self).__init__(message, *args, **kwargs)


class TokenExpiredException(DomainException):
    code = "TOKEN_EXPIRED"
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JwtUtils:
    JWT_PUBLIC_KEY = ""

    def get_token_payload(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, self.JWT_PUBLIC_KEY, algorithms="RS256")
        except ExpiredSignatureError:
            raise TokenExpiredException("The supplied token is expired!")
        except JWTError:
            raise TokenInvalidException()
        if payload["typ"] not in ["access", "refresh"]:
            raise TokenInvalidException()
        return payload
