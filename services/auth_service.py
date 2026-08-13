"""
Authentication Service.

Provides password hashing, verification, token generation, token validation,
and user authentication logic for the IRS platform.
"""

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Optional

from database.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Secret key for HMAC token signing
SECRET_KEY = "irs_secret_jwt_key_super_secure_production"
TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days


def hash_password(password: str) -> str:
    """
    Securely hash password using PBKDF2 with SHA-256 and a random salt.

    Returns:
        Formatted string: pbkdf2_sha256$iterations$salt_hex$hash_hex
    """
    salt = secrets.token_bytes(16)
    iterations = 100000
    derived = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify plain password against stored PBKDF2 hash.
    """
    try:
        parts = password_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = parts[3]

        derived = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(derived.hex(), expected_hash)
    except Exception as e:
        logger.error("Error verifying password: %s", e)
        return False


def create_token(payload: dict) -> str:
    """
    Create a signed base64url token with expiration.
    """
    payload_copy = dict(payload)
    payload_copy["exp"] = int(time.time()) + TOKEN_EXPIRY_SECONDS
    payload_json = json.dumps(payload_copy, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')

    signature = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode token, returning payload if valid.
    """
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts[0], parts[1]

        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None

        padding = '=' * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
        payload = json.loads(payload_json)

        if payload.get("exp", 0) < time.time():
            logger.warning("Token expired")
            return None

        return payload
    except Exception as e:
        logger.error("Token verification error: %s", e)
        return None


class AuthService:
    """Service handling user authentication workflows."""

    def __init__(self) -> None:
        self._user_repo = UserRepository()

    def close(self) -> None:
        self._user_repo.close()

    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """
        Authenticate user by username and password.

        Returns user dict if valid and active, else None.
        """
        user = self._user_repo.get_user_by_username(username)
        if not user:
            logger.warning("Authentication failed: username %s not found", username)
            return None

        if not user.get("is_active", True):
            logger.warning("Authentication failed: user %s is inactive", username)
            return None

        if not verify_password(password, user["password_hash"]):
            logger.warning("Authentication failed: invalid password for %s", username)
            return None

        return user

    def login(self, username: str, password: str) -> Optional[dict]:
        """
        Login user and return response dict with user info and access_token.
        """
        user = self.authenticate_user(username, password)
        if not user:
            return None

        token_payload = {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "employee_id": user.get("employee_id"),
        }
        token = create_token(token_payload)

        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "employee_id": user.get("employee_id"),
            "access_token": token,
            "token_type": "bearer",
        }

    def register_user(
        self,
        username: str,
        password: str,
        role: str = "EMPLOYEE",
        employee_id: Optional[int] = None,
    ) -> dict:
        """
        Register a new user and return response dict with user info and access_token.
        """
        clean_username = username.strip()
        if not clean_username:
            raise ValueError("Username cannot be empty")

        if len(clean_username) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters long")

        role_upper = role.upper()
        if role_upper not in ("EMPLOYEE", "HR"):
            raise ValueError("Role must be either EMPLOYEE or HR")

        # Check if username already exists
        existing = self._user_repo.get_user_by_username(clean_username)
        if existing:
            raise ValueError(f"Username '{clean_username}' is already taken")

        # Default employee_id if role is EMPLOYEE and employee_id is not provided
        if role_upper == "EMPLOYEE" and employee_id is None:
            employee_id = 1

        # Hash password and save user
        hashed_pwd = hash_password(password)
        user_record = self._user_repo.create_user(
            username=clean_username,
            password_hash=hashed_pwd,
            role=role_upper,
            employee_id=employee_id if role_upper == "EMPLOYEE" else None,
        )

        token_payload = {
            "user_id": user_record["user_id"],
            "username": user_record["username"],
            "role": user_record["role"],
            "employee_id": user_record.get("employee_id"),
        }
        token = create_token(token_payload)

        return {
            "user_id": user_record["user_id"],
            "username": user_record["username"],
            "role": user_record["role"],
            "employee_id": user_record.get("employee_id"),
            "access_token": token,
            "token_type": "bearer",
            "message": "User registered successfully",
        }

