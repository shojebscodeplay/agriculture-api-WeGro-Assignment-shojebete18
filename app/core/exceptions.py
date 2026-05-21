import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class InvalidFilterError(HTTPException):
    def __init__(self, field: str, value: str, allowed: list):
        super().__init__(
            status_code=422,
            detail={
                "error": "Invalid filter value",
                "field": field,
                "value": value,
                "allowed_values": allowed
            }
        )
        logger.warning(f"Invalid filter — field: {field}, value: {value}")


class RecordNotFoundError(HTTPException):
    def __init__(self, resource: str, identifier):
        super().__init__(
            status_code=404,
            detail={
                "error": "Record not found",
                "resource": resource,
                "identifier": identifier
            }
        )
        logger.warning(f"Not found — resource: {resource}, id: {identifier}")


class DatabaseError(HTTPException):
    def __init__(self, message: str = "Database query failed"):
        super().__init__(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": message
            }
        )
        logger.error(f"Database error: {message}")


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} — path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Unexpected server error",
            "message": "Something went wrong. Please try again later."
        }
    )