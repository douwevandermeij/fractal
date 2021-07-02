class DomainException(Exception):
    def __init__(
        self, message, code=None, status_code=None, payload=None, headers=None
    ):
        super(DomainException, self).__init__(message)
        self.message = message
        if status_code:
            self.status_code = status_code
        if code:
            self.code = code
        self.payload = payload
        self.headers = headers


class AggregateRootError(DomainException):
    code = "AGGREGATE_ROOT_ERROR"
    status_code = 405

    def __init__(self, message=None):
        if not message:
            message = "Actions can only be taken on aggregate root objects."
        super(AggregateRootError, self).__init__(message)
