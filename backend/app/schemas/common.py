from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard unified API response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Standard error response structure."""
    success: bool = False
    detail: str
    code: Optional[str] = None
