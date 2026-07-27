"""
Grade repository module.

Handles all database queries related to grade requirements.
Uses a shared pooled connection borrowed from the pool at construction time.
"""

import logging
from typing import Optional

import mysql.connector

from database.db_connection import get_connection

logger = logging.getLogger(__name__)


class GradeRepository:
    """Repository for grade-requirement-related database operations."""

    def __init__(self) -> None:
        """Initialise the repository and borrow a connection from the pool."""
        self._conn = get_connection()

    def close(self) -> None:
        """Return the connection back to the pool."""
        if self._conn and self._conn.is_connected():
            self._conn.close()

    def get_grade(self, grade_id: int) -> Optional[dict]:
        """
        Fetch a grade record by its primary key.

        Args:
            grade_id: The primary key of the grade.

        Returns:
            A dict with grade_id, grade_name, description, or None if not found.
        """
        query = """
            SELECT grade_id, grade_name, description
            FROM grades
            WHERE grade_id = %s
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (grade_id,))
            row = cursor.fetchone()
            cursor.close()
            return row
        except mysql.connector.Error as e:
            logger.error("get_grade(%s) failed: %s", grade_id, e)
            raise

    def get_grade_skills(self, grade_id: int) -> list[dict]:
        """
        Fetch all skill requirements for a given grade.

        Args:
            grade_id: The primary key of the grade.

        Returns:
            List of dicts with skill_name, required_level, weight, mandatory.
        """
        query = """
            SELECT
                s.skill_name,
                s.category,
                gsr.required_level,
                gsr.weight,
                gsr.mandatory
            FROM grade_skill_requirements gsr
            JOIN skills s ON gsr.skill_id = s.skill_id
            WHERE gsr.grade_id = %s
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (grade_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_grade_skills(%s) failed: %s", grade_id, e)
            raise

    def get_grade_certifications(self, grade_id: int) -> list[dict]:
        """
        Fetch all certification requirements for a given grade.

        Args:
            grade_id: The primary key of the grade.

        Returns:
            List of dicts with certification_name, mandatory.
        """
        query = """
            SELECT
                c.certification_name,
                c.provider,
                gcr.mandatory
            FROM grade_certification_requirements gcr
            JOIN certifications c ON gcr.certification_id = c.certification_id
            WHERE gcr.grade_id = %s
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (grade_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_grade_certifications(%s) failed: %s", grade_id, e)
            raise

    def get_grade_project_requirement(self, grade_id: int) -> Optional[dict]:
        """
        Fetch the project and experience requirements for a given grade.

        Args:
            grade_id: The primary key of the grade.

        Returns:
            A dict with minimum_projects, minimum_lead_projects,
            minimum_experience, or None if not found.
        """
        query = """
            SELECT
                minimum_projects,
                minimum_lead_projects,
                minimum_experience
            FROM grade_project_requirements
            WHERE grade_id = %s
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (grade_id,))
            row = cursor.fetchone()
            cursor.close()
            return row
        except mysql.connector.Error as e:
            logger.error("get_grade_project_requirement(%s) failed: %s", grade_id, e)
            raise
