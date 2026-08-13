"""
Authentication API routes for login, logout, and current user info.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.auth_service import AuthService
from api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "aarav"})
    password: str = Field(..., json_schema_extra={"example": "password123"})


class LoginResponse(BaseModel):
    user_id: int
    username: str
    role: str
    employee_id: Optional[int] = None
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "new_user"})
    password: str = Field(..., json_schema_extra={"example": "password123"})
    role: str = Field("EMPLOYEE", json_schema_extra={"example": "EMPLOYEE"})
    employee_id: Optional[int] = Field(None, json_schema_extra={"example": 1})


class RegisterResponse(BaseModel):
    user_id: int
    username: str
    role: str
    employee_id: Optional[int] = None
    access_token: str
    token_type: str = "bearer"
    message: str = "User registered successfully"


class UserMeResponse(BaseModel):
    user_id: int
    username: str
    role: str
    employee_id: Optional[int] = None


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account for an employee or HR role and return session token.",
)
def register(credentials: RegisterRequest):
    logger.info("Registration attempt for username: %s, role: %s", credentials.username, credentials.role)
    auth_svc = AuthService()
    try:
        result = auth_svc.register_user(
            username=credentials.username,
            password=credentials.password,
            role=credentials.role,
            employee_id=credentials.employee_id,
        )
        return RegisterResponse(**result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    finally:
        auth_svc.close()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate employee or HR user and return session token and role details.",
)
def login(credentials: LoginRequest):
    logger.info("Login attempt for username: %s", credentials.username)
    auth_svc = AuthService()
    try:
        result = auth_svc.login(credentials.username, credentials.password)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        return LoginResponse(**result)
    finally:
        auth_svc.close()


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Logout authenticated user and invalidate session context.",
)
def logout(current_user: dict = Depends(get_current_user)):
    logger.info("Logout for user: %s", current_user.get("username"))
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Return details of the currently authenticated user.",
)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserMeResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        role=current_user["role"],
        employee_id=current_user.get("employee_id"),
    )
