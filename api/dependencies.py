"""
Authentication & Authorization dependencies for FastAPI endpoints.

Enforces Role-Based Access Control (RBAC) at the backend layer.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status, Header
from services.auth_service import verify_token

logger = logging.getLogger(__name__)


def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract bearer token from Authorization header or custom header."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    elif len(parts) == 1:
        return parts[0]
    return None


def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency that returns the current authenticated user payload.

    Raises:
        HTTPException(401): If missing or invalid token.
    """
    token = get_token_from_header(authorization)
    if not token:
        # Check query param for fallback
        token = request.query_params.get("token")

    if not token:
        logger.warning("Unauthenticated request to %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_payload = verify_token(token)
    if not user_payload:
        logger.warning("Invalid token provided for %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_payload


def require_hr(current_user: dict = None) -> dict:
    """
    Dependency that restricts endpoint access to HR role only.

    Raises:
        HTTPException(403): If user role is not HR.
    """
    if not current_user or current_user.get("role") != "HR":
        logger.warning("Forbidden non-HR access attempt by user %s (role=%s)",
                       current_user.get("username") if current_user else "unknown",
                       current_user.get("role") if current_user else "none")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: HR access required",
        )
    return current_user


def require_employee(current_user: dict = None) -> dict:
    """
    Dependency that restricts endpoint access to EMPLOYEE role only.

    Raises:
        HTTPException(403): If user role is not EMPLOYEE or employee_id is missing.
    """
    if not current_user or current_user.get("role") != "EMPLOYEE" or not current_user.get("employee_id"):
        logger.warning("Forbidden non-employee access attempt by user %s",
                       current_user.get("username") if current_user else "unknown")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Employee access required",
        )
    return current_user
