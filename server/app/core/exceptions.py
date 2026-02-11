import uuid
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(status_code=status_code, detail=detail)


# ─── Generic errors ──────────────────────────────────────────────────────────

class ResourceNotFoundException(AppException):
    def __init__(self, resource_type: str, resource_id: uuid.UUID | str):
        super().__init__(
            detail=f"{resource_type} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidInputException(AppException):
    def __init__(self, message: str):
        super().__init__(
            detail=f"Invalid input: {message}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# ─── User errors ─────────────────────────────────────────────────────────────

class UserCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            detail="Incorrect email / password",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserEmailAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            detail=f"User with email '{email}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class UsernameAlreadyExistsException(AppException):
    def __init__(self, username: str):
        super().__init__(
            detail=f"User with username '{username}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class UserNotFoundException(AppException):
    def __init__(self, email: str):
        super().__init__(
            detail=f"User with email '{email}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserTokenInvalidException(AppException):
    def __init__(self):
        super().__init__(
            detail="Token out of date or invalid",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


# ─── Vote errors ─────────────────────────────────────────────────────────────

class VoteAccessDeniedException(AppException):
    def __init__(self, vote_id: uuid.UUID):
        super().__init__(
            detail=f"You don't have access to vote {vote_id}",
            status_code=status.HTTP_403_FORBIDDEN,
        )
