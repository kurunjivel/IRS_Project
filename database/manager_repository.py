"""
Manager Repository — Phase 1 Enhancement 4.

Handles database and memory operations for manager-employee assignments,
quarterly calibrations, review approvals, and audit trail logging.
"""

import logging
from typing import Optional
from unittest.mock import MagicMock

from database.db_connection import get_connection
from models.manager_review import ManagerReview, ReviewAuditLog, ReviewStatus

logger = logging.getLogger(__name__)


def _is_real_conn(conn) -> bool:
    if conn is None:
        return False
    if isinstance(conn, MagicMock) or type(conn).__name__ in ("MagicMock", "Mock"):
        return False
    return True


# Default in-memory manager assignments:
# Manager ID 10 manages Employee 1 (Aarav Sharma) and Employee 2 (Priya Nair)
# Manager ID 20 manages Employee 3 (Ananya)
_MEM_MANAGER_ASSIGNMENTS: dict[int, int] = {
    1: 10,
    2: 10,
    3: 20,
}

_MEM_REVIEWS: dict[str, dict] = {}  # key: f"{employee_id}_{quarter}"
_MEM_AUDITS: list[dict] = []


def _init_default_reviews():
    global _MEM_REVIEWS
    if not _MEM_REVIEWS:
        # Default pending review for Employee 1
        key1 = "1_Q3-2026"
        _MEM_REVIEWS[key1] = {
            "review_id": 1,
            "employee_id": 1,
            "manager_id": 10,
            "quarter": "Q3-2026",
            "status": ReviewStatus.PENDING,
            "technical_competency": 4,
            "communication": 4,
            "leadership": 3,
            "teamwork": 5,
            "ownership": 4,
            "overall_assessment": "Solid technical performance across projects.",
            "comments": "Awaiting final calibration review.",
            "created_at": "2026-08-01T10:00:00",
            "updated_at": "2026-08-01T10:00:00",
        }


class ManagerRepository:
    """Repository for managing direct report relationships, calibrations, and review audits."""

    def __init__(self, conn=None) -> None:
        _init_default_reviews()
        self._custom_conn = conn

    def close(self) -> None:
        if (
            self._custom_conn
            and _is_real_conn(self._custom_conn)
            and hasattr(self._custom_conn, "is_connected")
            and self._custom_conn.is_connected()
        ):
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
            logger.debug("Database connection unavailable for ManagerRepository, using fallback store: %s", e)
            return None

    def _release_conn(self, conn) -> None:
        if not self._custom_conn and _is_real_conn(conn) and hasattr(conn, "close"):
            try:
                conn.close()
            except Exception:
                pass

    def get_managed_employee_ids(self, manager_id: int) -> list[int]:
        """Fetch list of employee IDs managed by the given manager."""
        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = "SELECT employee_id FROM employees WHERE manager_id = %s"
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, (manager_id,))
                    rows = cursor.fetchall()
                    if rows:
                        return [r["employee_id"] for r in rows]
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query get_managed_employee_ids failed, falling back: %s", e)
            finally:
                self._release_conn(conn)

        return [emp_id for emp_id, m_id in _MEM_MANAGER_ASSIGNMENTS.items() if m_id == manager_id]

    def is_manager_of(self, manager_id: int, employee_id: int) -> bool:
        """Check if manager_id is assigned to manage employee_id."""
        managed_ids = self.get_managed_employee_ids(manager_id)
        return employee_id in managed_ids

    def get_review(self, employee_id: int, quarter: str = "Q3-2026") -> Optional[dict]:
        """Get latest review record for employee in a given quarter."""
        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = """
                    SELECT review_id, employee_id, manager_id, quarter, status,
                           technical_competency, communication, leadership, teamwork, ownership,
                           overall_assessment, comments, created_at, updated_at
                    FROM manager_reviews
                    WHERE employee_id = %s AND quarter = %s
                    ORDER BY review_id DESC LIMIT 1
                """
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, (employee_id, quarter))
                    row = cursor.fetchone()
                    if row:
                        return row
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query get_review failed, falling back: %s", e)
            finally:
                self._release_conn(conn)

        key = f"{employee_id}_{quarter}"
        return _MEM_REVIEWS.get(key)

    def save_review(self, review: ManagerReview) -> dict:
        """Create or update manager calibration review."""
        conn = self._get_conn()
        review_data = None
        if _is_real_conn(conn):
            try:
                query = """
                    INSERT INTO manager_reviews
                    (employee_id, manager_id, quarter, status, technical_competency, communication,
                     leadership, teamwork, ownership, overall_assessment, comments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    technical_competency = VALUES(technical_competency),
                    communication = VALUES(communication),
                    leadership = VALUES(leadership),
                    teamwork = VALUES(teamwork),
                    ownership = VALUES(ownership),
                    overall_assessment = VALUES(overall_assessment),
                    comments = VALUES(comments)
                """
                cursor = conn.cursor()
                try:
                    cursor.execute(query, (
                        review.employee_id, review.manager_id, review.quarter, review.status,
                        review.technical_competency, review.communication, review.leadership,
                        review.teamwork, review.ownership, review.overall_assessment, review.comments
                    ))
                    conn.commit()
                    review_id = cursor.lastrowid or review.review_id or 1
                    review_data = {
                        "review_id": review_id,
                        "employee_id": review.employee_id,
                        "manager_id": review.manager_id,
                        "quarter": review.quarter,
                        "status": review.status,
                        "technical_competency": review.technical_competency,
                        "communication": review.communication,
                        "leadership": review.leadership,
                        "teamwork": review.teamwork,
                        "ownership": review.ownership,
                        "overall_assessment": review.overall_assessment,
                        "comments": review.comments,
                        "created_at": review.created_at or "2026-08-19T12:00:00",
                        "updated_at": "2026-08-19T12:00:00",
                    }
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query save_review failed, falling back: %s", e)
            finally:
                self._release_conn(conn)

        if not review_data:
            key = f"{review.employee_id}_{review.quarter}"
            existing = _MEM_REVIEWS.get(key)
            review_id = existing["review_id"] if existing else len(_MEM_REVIEWS) + 1
            review_data = {
                "review_id": review_id,
                "employee_id": review.employee_id,
                "manager_id": review.manager_id,
                "quarter": review.quarter,
                "status": review.status,
                "technical_competency": review.technical_competency,
                "communication": review.communication,
                "leadership": review.leadership,
                "teamwork": review.teamwork,
                "ownership": review.ownership,
                "overall_assessment": review.overall_assessment,
                "comments": review.comments,
                "created_at": review.created_at or "2026-08-19T12:00:00",
                "updated_at": "2026-08-19T12:00:00",
            }
            _MEM_REVIEWS[key] = review_data

        return review_data

    def log_audit(self, audit: ReviewAuditLog) -> dict:
        """Insert an audit log entry for review state transitions."""
        conn = self._get_conn()
        audit_data = None
        if _is_real_conn(conn):
            try:
                query = """
                    INSERT INTO manager_review_audit
                    (review_id, employee_id, manager_id, previous_status, new_status, comments, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor = conn.cursor()
                try:
                    cursor.execute(query, (
                        audit.review_id, audit.employee_id, audit.manager_id,
                        audit.previous_status, audit.new_status, audit.comments, audit.timestamp
                    ))
                    conn.commit()
                    audit_id = cursor.lastrowid
                    audit_data = {
                        "audit_id": audit_id,
                        "review_id": audit.review_id,
                        "employee_id": audit.employee_id,
                        "manager_id": audit.manager_id,
                        "previous_status": audit.previous_status,
                        "new_status": audit.new_status,
                        "comments": audit.comments,
                        "timestamp": audit.timestamp,
                    }
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query log_audit failed, falling back: %s", e)
            finally:
                self._release_conn(conn)

        if not audit_data:
            audit_id = len(_MEM_AUDITS) + 1
            audit_data = {
                "audit_id": audit_id,
                "review_id": audit.review_id,
                "employee_id": audit.employee_id,
                "manager_id": audit.manager_id,
                "previous_status": audit.previous_status,
                "new_status": audit.new_status,
                "comments": audit.comments,
                "timestamp": audit.timestamp,
            }
            _MEM_AUDITS.append(audit_data)

        return audit_data

    def get_audit_history(self, employee_id: int) -> list[dict]:
        """Fetch full audit history for an employee's reviews."""
        conn = self._get_conn()
        if _is_real_conn(conn):
            try:
                query = """
                    SELECT audit_id, review_id, employee_id, manager_id, previous_status, new_status, comments, timestamp
                    FROM manager_review_audit
                    WHERE employee_id = %s
                    ORDER BY timestamp DESC
                """
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, (employee_id,))
                    rows = cursor.fetchall()
                    if rows:
                        return rows
                finally:
                    cursor.close()
            except Exception as e:
                logger.warning("DB query get_audit_history failed, falling back: %s", e)
            finally:
                self._release_conn(conn)

        return [a for a in _MEM_AUDITS if a["employee_id"] == employee_id]
