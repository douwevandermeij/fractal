from pydantic import BaseModel


class ErrorMessage(BaseModel):
    code: str
    message: str
