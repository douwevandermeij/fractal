class DomainException(Exception):
    def __init__(
        self, message, code=None, status_code=None, payload=None, headers=None
    ):
        Exception.__init__(self)
        self.message = message
        if status_code:
            self.status_code = status_code
        if code:
            self.code = code
        self.payload = payload
        self.headers = headers
