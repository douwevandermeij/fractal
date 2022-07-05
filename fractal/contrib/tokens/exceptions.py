from fractal.core.exceptions import DomainException


class TokenInvalidException(DomainException):
    code = "TOKEN_INVALID"
    status_code = 401

    def __init__(self, message=None):
        if not message:
            message = "The supplied token is invalid!"
        super(TokenInvalidException, self).__init__(message)


class TokenExpiredException(DomainException):
    code = "TOKEN_EXPIRED"
    status_code = 401

    def __init__(self, message=None):
        if not message:
            message = "The supplied token is expired!"
        super(TokenExpiredException, self).__init__(message)


class NotAllowedException(DomainException):
    code = "NOT_ALLOWED_ERROR"
    status_code = 401
