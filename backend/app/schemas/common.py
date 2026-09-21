from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    errorCode: str
    message: str
    details: Any | None = None


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any | None = None
    message: str | None = None
