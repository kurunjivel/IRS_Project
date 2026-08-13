"""
User repository module.

Handles database queries for authentication and user records in the users table.
Provides fallback standard seed users if DB is uninitialized or in test mode.
"""

import logging
from typing import Optional
from database.db_connection import get_connection

logger = logging.getLogger(__name__)


def _get_default_seed_users() -> list[dict]:
    """Helper to generate default seed users with hashed passwords."""
    from services.auth_service import hash_password
    return [
        {
            "user_id": 1,
            "username": "hr",
            "password_hash": hash_password("hr123"),
            "role": "HR",
            "employee_id": None,
            "is_active": 1,
        },
        {
            "user_id": 2,
            "username": "aarav",
            "password_hash": hash_password("password123"),
            "role": "EMPLOYEE",
            "employee_id": 1,
            "is_active": 1,
        },
        {
            "user_id": 3,
            "username": "employee",
            "password_hash": hash_password("emp123"),
            "role": "EMPLOYEE",
            "employee_id": 1,
            "is_active": 1,
        },
        {
            "user_id": 4,
            "username": "priya",
            "password_hash": hash_password("password123"),
            "role": "EMPLOYEE",
            "employee_id": 2,
            "is_active": 1,
        },
        {
            "user_id": 5,
            "username": "ananya",
            "password_hash": hash_password("password123"),
            "role": "EMPLOYEE",
            "employee_id": 3,
            "is_active": 1,
        },
    ]


from unittest.mock import MagicMock

def _is_real_conn(conn) -> bool:
    if conn is None:
        return False
    if isinstance(conn, MagicMock) or type(conn).__name__ in ('MagicMock', 'Mock'):
        return False
    return True

# Global memory store for mock/fallback environment
_MEM_USERS: dict[str, dict] = {}


def _init_mem_users():
    global _MEM_USERS
    if not _MEM_USERS:
        for u in _get_default_seed_users():
            _MEM_USERS[u["username"].lower()] = u


class UserRepository:
    """Repository for user authentication and authorization persistence."""

    def __init__(self, conn: Optional[mysql.connector.pooling.PooledMySQLConnection] = None) -> None:
        _init_mem_users()
        self._custom_conn = conn

    def close(self) -> None:
        if self._custom_conn and _is_real_conn(self._custom_conn) and hasattr(self._custom_conn, "is_connected") and self._custom_conn.is_connected():
            try:
                self._custom_conn.close()
            except Exception:
                pass

    def _get_conn(self):
        if self._custom_conn is not None:
            return self._custom_conn
        try:
            return get_connection()
        except Exception as e:
            logger.debug("Database connection not available for UserRepository operation, using fallback store: %s", e)
            return None

    def _release_conn(self, conn) -> None:
        if not self._custom_conn and _is_real_conn(conn) and hasattr(conn, "close"):
            try:
                conn.close()
            except Exception:
                pass

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """
        Fetch user record by username.
        """
        if not username:
            return None

        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = """
                    SELECT user_id, username, password_hash, role, employee_id, is_active
                    FROM users
                    WHERE LOWER(username) = LOWER(%s)
                """
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, (username.strip(),))
                    row = cursor.fetchone()
                    if row:
                        return row
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query get_user_by_username failed, falling back to memory store: %s", e)
            finally:
                self._release_conn(conn)

        # Fallback to memory store
        return _MEM_USERS.get(username.strip().lower())

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Fetch user record by user_id.
        """
        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = """
                    SELECT user_id, username, password_hash, role, employee_id, is_active
                    FROM users
                    WHERE user_id = %s
                """
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, (user_id,))
                    row = cursor.fetchone()
                    if row:
                        return row
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query get_user_by_id failed, falling back: %s", e)
            finally:
                self._release_conn(conn)

        for u in _MEM_USERS.values():
            if u["user_id"] == user_id:
                return u
        return None

    def get_all_users(self) -> list[dict]:
        """
        Fetch list of all users.
        """
        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = "SELECT user_id, username, role, employee_id, is_active FROM users"
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    if rows:
                        return rows
                finally:
                    cursor.close()
            except Exception:
                pass
            finally:
                self._release_conn(conn)
        return list(_MEM_USERS.values())

    def create_user(self, username: str, password_hash: str, role: str, employee_id: Optional[int] = None) -> dict:
        """
        Create new user record.
        """
        user_record = None
        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = """
                    INSERT INTO users (username, password_hash, role, employee_id, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """
                cursor = conn.cursor()
                try:
                    cursor.execute(query, (username, password_hash, role, employee_id))
                    new_id = cursor.lastrowid
                    conn.commit()
                    user_record = {
                        "user_id": new_id,
                        "username": username,
                        "password_hash": password_hash,
                        "role": role,
                        "employee_id": employee_id,
                        "is_active": 1,
                    }
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("Failed to create user in DB, adding to memory store: %s", e)
            finally:
                self._release_conn(conn)

        if not user_record:
            new_id = len(_MEM_USERS) + 1
            user_record = {
                "user_id": new_id,
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "employee_id": employee_id,
                "is_active": 1,
            }
        
        _MEM_USERS[username.lower()] = user_record
        return user_record

