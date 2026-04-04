from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import ingest
from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    ParseFailureError,
    UnsupportedFormatError,
)
from app.core.logging import setup_logging
from app.models.responses import ErrorResponse

setup_logging(debug=settings.debug)

app = FastAPI(
    title=settings.app_name,
    desciption="multi-format document ingestion and parsing API",
    version="1.0.0",
)

app.include_router(ingest.router)


@app.exception_handler(UnsupportedFormatError)
async def unsupported_format_handler(request: Request, exc: UnsupportedFormatError):
    return JSONResponse(
        status_code=415,
        content=ErrorResponse(
            error="UnsupportedFormat",
            detail=str(exc),
        ).model_dump(),
    )


@app.exception_handler(ParseFailureError)
async def parse_failure_handler(request: Request, exc: ParseFailureError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ParseFailure",
            detail=str(exc),
        ).model_dump(),
    )


@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(request: Request, exc: FileTooLargeError):
    return JSONResponse(
        status_code=413,
        content=ErrorResponse(
            error="FileTooLarge",
            detail=str(exc),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            detail="An unexpected error occurred.",
        ).model_dump(),
    )


@app.get("/health", tags=["meta"])
def health_check():
    return {"status": "ok", "app": settings.app_name}
