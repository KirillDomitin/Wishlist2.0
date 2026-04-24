from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """HTTP 404 Not Found error."""

    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedError(HTTPException):
    """HTTP 401 Unauthorized error."""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenError(HTTPException):
    """HTTP 403 Forbidden error."""

    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictError(HTTPException):
    """HTTP 409 Conflict error."""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
