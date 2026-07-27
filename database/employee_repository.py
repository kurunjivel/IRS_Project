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

    def __init__(self) -> None:
        """Initialise the repository and borrow a connection from the pool."""
        self._conn = get_connection()

    def close(self) -> None:
        """Return the connection back to the pool."""
        if self._conn and self._conn.is_connected():
            self._conn.close()

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
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (employee_id,))
            row = cursor.fetchone()
            cursor.close()
            return row
        except mysql.connector.Error as e:
            logger.error("get_employee(%s) failed: %s", employee_id, e)
            raise

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
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (employee_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_employee_skills(%s) failed: %s", employee_id, e)
            raise

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
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (employee_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_employee_certifications(%s) failed: %s", employee_id, e)
            raise

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
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (employee_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_employee_projects(%s) failed: %s", employee_id, e)
            raise
