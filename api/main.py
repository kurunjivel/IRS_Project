"""
IRS FastAPI Application — Phase 7 API Layer.

Entry point for the Intelligent Recommendation System RESTful API.
Configures FastAPI routes, custom exception handling, logging middleware,
and Pydantic response models.
"""

import logging
import time
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from services.gap_analysis_service import (
    EmployeeNotFoundError,
    GradeNotFoundError,
)
from api.routes import (
    employee_router,
    gap_analysis_router,
    readiness_router,
    prediction_router,
    recommendations_router,
    career_analysis_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("irs_api")

app = FastAPI(
    title="Intelligent Recommendation System (IRS) API",
    version="1.0.0",
    description="RESTful API layer for promotion readiness, gap analysis, ML prediction, and hybrid recommendations.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------
@app.exception_handler(EmployeeNotFoundError)
async def employee_not_found_handler(request: Request, exc: EmployeeNotFoundError):
    """Handle missing employee errors with HTTP 404."""
    logger.warning("EmployeeNotFoundError at %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "status_code": status.HTTP_404_NOT_FOUND,
        },
    )


@app.exception_handler(GradeNotFoundError)
async def grade_not_found_handler(request: Request, exc: GradeNotFoundError):
    """Handle missing grade requirement errors with HTTP 404."""
    logger.warning("GradeNotFoundError at %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "status_code": status.HTTP_404_NOT_FOUND,
        },
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle missing ML model file errors with HTTP 503."""
    logger.error("FileNotFoundError at %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": f"Service unavailable: {str(exc)}",
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with clean JSON responses."""
    logger.warning("HTTPException %d at %s: %s", exc.status_code, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected internal server errors with HTTP 500."""
    logger.exception("Unhandled exception at %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred processing your request.",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming HTTP request details and execution duration."""
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error("%s %s -> unhandled error: %s (%.2f ms)", request.method, request.url.path, exc, duration_ms)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred processing your request.",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )
    duration_ms = (time.perf_counter() - start_time) * 1000.0
    logger.info(
        "%s %s -> status %d (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Route Inclusion
# ---------------------------------------------------------------------------
app.include_router(employee_router)
app.include_router(gap_analysis_router)
app.include_router(readiness_router)
app.include_router(prediction_router)
app.include_router(recommendations_router)
app.include_router(career_analysis_router)


# ---------------------------------------------------------------------------
# Health / Root Endpoint
# ---------------------------------------------------------------------------
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check endpoint",
    status_code=status.HTTP_200_OK,
)
def health_check():
    """Simple API health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}
