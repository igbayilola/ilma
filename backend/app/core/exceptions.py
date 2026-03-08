"""Global exception handlers for the FastAPI application."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.response import err


class AppException(Exception):
    """Base application exception with structured error info."""

    def __init__(
        self,
        status_code: int = 400,
        code: str = "BAD_REQUEST",
        message: str = "An error occurred",
        details: any = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource", id: str = ""):
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=f"{resource} not found" + (f": {id}" if id else ""),
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(status_code=403, code="FORBIDDEN", message=message)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(status_code=409, code="CONFLICT", message=message)


class RateLimitException(AppException):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(status_code=429, code="RATE_LIMITED", message=message)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=err(code=exc.code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=err(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, _exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=err(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
            ),
        )
