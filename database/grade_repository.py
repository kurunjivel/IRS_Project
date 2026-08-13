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
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (grade_id,))
                row = cursor.fetchone()
                return row
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_grade(%s) failed: %s", grade_id, e)
            raise
        finally:
            self._release_conn(conn)

    def get_all_grades(self) -> list[dict]:
        """
        Fetch all available grades/roles.
        """
        query = """
            SELECT grade_id, grade_name, description
            FROM grades
            ORDER BY grade_id ASC
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
            logger.error("get_all_grades failed: %s", e)
            raise
        finally:
            self._release_conn(conn)

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
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (grade_id,))
                rows = cursor.fetchall()
                return rows
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_grade_skills(%s) failed: %s", grade_id, e)
            raise
        finally:
            self._release_conn(conn)

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
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (grade_id,))
                rows = cursor.fetchall()
                return rows
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_grade_certifications(%s) failed: %s", grade_id, e)
            raise
        finally:
            self._release_conn(conn)

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
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, (grade_id,))
                row = cursor.fetchone()
                return row
            finally:
                cursor.close()
        except mysql.connector.Error as e:
            logger.error("get_grade_project_requirement(%s) failed: %s", grade_id, e)
            raise
        finally:
            self._release_conn(conn)
