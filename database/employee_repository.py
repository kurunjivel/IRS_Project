"""
Employee repository module.

Handles all database queries related to employees.
Uses a shared pooled connection borrowed from the pool at construction time.
"""

import logging
from typing import Optional

import mysql.connector

from database.db_connection import get_connection

logger = logging.getLogger(__name__)


class EmployeeRepository:
    """Repository for employee-related database operations."""

    def __init__(self, conn: Optional[mysql.connector.pooling.PooledMySQLConnection] = None) -> None:
        """Initialise repository with an optional custom connection."""
        self._custom_conn = conn

    def close(self) -> None:
        """Return the custom connection back to the pool if owned by this instance."""
        if self._custom_conn and hasattr(self._custom_conn, "is_connected") and self._custom_conn.is_connected():
            try:
                self._custom_conn.close()
            except Exception:
                pass

    def _get_conn(self):
        return self._custom_conn or get_connection()

    def _release_conn(self, conn) -> None:
        if not self._custom_conn and conn and hasattr(conn, "close"):
            try:
                conn.close()
            except Exception:
                pass

    def get_employee(self, employee_id: int) -> Optional[dict]:
        """
        Fetch core employee details including current and target grade.

        Args:
            employee_id: The primary key of the employee.

        Returns:
            A dict with employee details, or None if not found.
        """
        query = """
            SELECT
                e.employee_id,
                e.employee_code,
                e.full_name,
                e.email,
                e.department,
                e.experience_years,
                e.performance_rating,
                e.joining_date,
                cg.grade_name   AS current_grade,
                cg.grade_id     AS current_grade_id,
                tg.grade_name   AS target_grade,
                tg.grade_id     AS target_grade_id
            FROM employees e
            JOIN grades cg ON e.current_grade_id = cg.grade_id
            JOIN grades tg ON e.target_grade_id  = tg.grade_id
            WHERE e.employee_id = %s
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (employee_id,))
                row = cursor.fetchone()
                return row
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_employee(%s) failed: %s", employee_id, e)
            raise
        finally:
            self._release_conn(conn)

    def get_all_employees(self) -> list[dict]:
        """
        Fetch all employees with current and target grade names.
        """
        query = """
            SELECT
                e.employee_id,
                e.employee_code,
                e.full_name,
                e.email,
                e.department,
                e.experience_years,
                e.performance_rating,
                e.joining_date,
                cg.grade_name   AS current_grade,
                cg.grade_id     AS current_grade_id,
                tg.grade_name   AS target_grade,
                tg.grade_id     AS target_grade_id
            FROM employees e
            JOIN grades cg ON e.current_grade_id = cg.grade_id
            JOIN grades tg ON e.target_grade_id  = tg.grade_id
            ORDER BY e.employee_id ASC
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_all_employees failed: %s", e)
            raise
        finally:
            self._release_conn(conn)

    def get_employee_skills(self, employee_id: int) -> list[dict]:
        """
        Fetch all skills the employee currently holds.

        Args:
            employee_id: The primary key of the employee.

        Returns:
            List of dicts with skill_name and skill_level.
        """
        query = """
            SELECT
                s.skill_name,
                s.category,
                es.skill_level
            FROM employee_skills es
            JOIN skills s ON es.skill_id = s.skill_id
            WHERE es.employee_id = %s
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (employee_id,))
                rows = cursor.fetchall()
                return rows
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_employee_skills(%s) failed: %s", employee_id, e)
            raise
        finally:
            self._release_conn(conn)

    def get_employee_certifications(self, employee_id: int) -> list[dict]:
        """
        Fetch all certifications the employee holds.

        Args:
            employee_id: The primary key of the employee.

        Returns:
            List of dicts with certification_name, status, completion_date.
        """
        query = """
            SELECT
                c.certification_name,
                c.provider,
                ec.status,
                ec.completion_date,
                ec.expiry_date
            FROM employee_certifications ec
            JOIN certifications c ON ec.certification_id = c.certification_id
            WHERE ec.employee_id = %s
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (employee_id,))
                rows = cursor.fetchall()
                return rows
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_employee_certifications(%s) failed: %s", employee_id, e)
            raise
        finally:
            self._release_conn(conn)

    def get_employee_projects(self, employee_id: int) -> list[dict]:
        """
        Fetch all projects the employee has participated in.

        Args:
            employee_id: The primary key of the employee.

        Returns:
            List of dicts with project_name, technology, role,
            lead_project, duration_months, project_rating.
        """
        query = """
            SELECT
                p.project_name,
                p.technology,
                p.difficulty,
                p.domain,
                ep.role,
                ep.lead_project,
                ep.duration_months,
                ep.project_rating
            FROM employee_projects ep
            JOIN projects p ON ep.project_id = p.project_id
            WHERE ep.employee_id = %s
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (employee_id,))
                rows = cursor.fetchall()
                return rows
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_employee_projects(%s) failed: %s", employee_id, e)
            raise
        finally:
            self._release_conn(conn)
