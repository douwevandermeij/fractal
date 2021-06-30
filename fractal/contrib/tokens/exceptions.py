from fractal.core.exceptions import DomainException


class TokenInvalidException(DomainException):
    code = "TOKEN_INVALID"
    status_code = 403


class TokenExpiredException(DomainException):
    code = "TOKEN_EXPIRED"
    status_code = 403
