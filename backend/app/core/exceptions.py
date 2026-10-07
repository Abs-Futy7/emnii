from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "application_error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.headers = headers
        super().__init__(message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Could not validate credentials") -> None:
        super().__init__(
            message,
            code="authentication_failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(
            message,
            code="authorization_failed",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="resource_conflict",
            status_code=status.HTTP_409_CONFLICT,
        )


class ConfigurationError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="configuration_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            message,
            code="resource_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidUploadError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="invalid_upload",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


class InvalidRequestError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="invalid_request",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


class UploadTooLargeError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="upload_too_large",
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        )


class ExternalServiceError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="external_service_unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


async def app_exception_handler(
    request: Request,
    exception: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        headers=exception.headers,
        content={
            "error": {
                "code": exception.code,
                "message": exception.message,
                "path": request.url.path,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
