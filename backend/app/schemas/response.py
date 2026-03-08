"""Standard API response envelope."""
from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


def ok(data: Any = None, message: str | None = None) -> dict:
    """Helper to build a success envelope."""
    return ApiResponse(success=True, data=data, message=message).model_dump(mode="json")


def err(code: str, message: str, details: Any = None) -> dict:
    """Helper to build an error envelope."""
    return ApiErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details)
    ).model_dump(mode="json")


def paginated(items: list, total: int, page: int, page_size: int) -> dict:
    """Helper to build a paginated success envelope."""
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ok(
        data=PaginatedData(
            items=items, total=total, page=page, page_size=page_size, pages=pages
        )
    )
