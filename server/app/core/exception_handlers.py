from fastapi.responses import JSONResponse
from fastapi import Request
import traceback


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle our custom AppException subclasses with consistent JSON format.
    
    Note: exc is typed as Exception for FastAPI compatibility, but will always
    be an AppException when this handler is called (due to registration).
    """
    # We can safely access these attributes because FastAPI routes 
    # AppException instances to this handler
    return JSONResponse(
        status_code=getattr(exc, "status_code", 500),
        content={"error": getattr(exc, "detail", str(exc)), "code": getattr(exc, "status_code", 500)}
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle standard FastAPI HTTPExceptions."""
    return JSONResponse(
        status_code=getattr(exc, "status_code", 500),
        content={"error": getattr(exc, "detail", str(exc)), "code": getattr(exc, "status_code", 500)}
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors. Log them and return generic 500."""
    print(f"[ERROR] Unexpected error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred", "code": 500}
    )