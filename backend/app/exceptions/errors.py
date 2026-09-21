class AppError(Exception):
    """Base for domain errors that should surface as structured API errors
    (spec §39: {success, errorCode, message})."""

    status_code: int = 400
    error_code: str = "APP_ERROR"

    def __init__(self, message: str, details: object | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class ValidationAppError(AppError):
    status_code = 422
    error_code = "VALIDATION_ERROR"


class UnsupportedFileTypeError(AppError):
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"


class FileTooLargeError(AppError):
    status_code = 413
    error_code = "FILE_TOO_LARGE"


class UnparsableResumeError(AppError):
    status_code = 422
    error_code = "INVALID_RESUME"


class QualityGateError(AppError):
    status_code = 422
    error_code = "QUALITY_GATE_FAILED"


class AuthError(AppError):
    status_code = 401
    error_code = "AUTH_ERROR"


class ConflictError(AppError):
    status_code = 409
    error_code = "CONFLICT"
