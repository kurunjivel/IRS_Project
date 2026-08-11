"""
Recommendation repository module.

Handles all database queries needed by the Phase 6 recommendation engine:
    - courses and learning_paths (for learning recommendations)
    - certifications (for certification recommendations)
    - projects (for project recommendations)
    - mentors (for mentorship recommendations)
    - recommendation_history (for deduplication / tracking)

Uses a shared pooled connection borrowed from the pool at construction time.
"""

import logging
from typing import Optional

import mysql.connector

from database.db_connection import get_connection

logger = logging.getLogger(__name__)


class RecommendationRepository:
    """Repository for recommendation-related database queries."""

    def __init__(self) -> None:
        """Initialise the repository and borrow a connection from the pool."""
        self._conn = get_connection()

    def close(self) -> None:
        """Return the connection back to the pool."""
        if self._conn and self._conn.is_connected():
            self._conn.close()

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------

    def get_courses_for_skill(self, skill_name: str) -> list[dict]:
        """
        Fetch courses that help develop a given skill.

        Args:
            skill_name: The skill to search courses for (case-insensitive).

        Returns:
            List of dicts with course_id, course_name, provider,
            duration_hours, difficulty_level, skill_name.
        """
        query = """
            SELECT
                c.course_id,
                c.course_name,
                c.provider,
                c.duration_hours,
                c.difficulty AS difficulty_level,
                c.difficulty,
                s.skill_name
            FROM courses c
            JOIN skills s ON c.skill_id = s.skill_id
            WHERE LOWER(s.skill_name) = LOWER(%s)
            ORDER BY FIELD(c.difficulty, 'Beginner', 'Intermediate', 'Advanced') ASC
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (skill_name,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_courses_for_skill(%s) failed: %s", skill_name, e)
            raise

    def get_all_courses(self) -> list[dict]:
        """
        Fetch all available courses.

        Returns:
            List of dicts with course_id, course_name, provider,
            duration_hours, difficulty_level, skill_name.
        """
        query = """
            SELECT
                c.course_id,
                c.course_name,
                c.provider,
                c.duration_hours,
                c.difficulty AS difficulty_level,
                c.difficulty,
                s.skill_name
            FROM courses c
            JOIN skills s ON c.skill_id = s.skill_id
            ORDER BY s.skill_name, FIELD(c.difficulty, 'Beginner', 'Intermediate', 'Advanced')
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_all_courses() failed: %s", e)
            raise

    # ------------------------------------------------------------------
    # Learning paths
    # ------------------------------------------------------------------

    def get_learning_paths_for_grade(self, grade_id: int) -> list[dict]:
        """
        Fetch learning paths associated with a target grade.

        Args:
            grade_id: The target grade primary key.

        Returns:
            List of dicts with path_id, path_name, description,
            estimated_duration_months, grade_name.
        """
        query = """
            SELECT
                lp.learning_path_id AS path_id,
                CONCAT(s.skill_name, ' Learning Path') AS path_name,
                c.course_name AS description,
                ROUND(c.duration_hours / 40.0, 1) AS estimated_duration_months,
                g.grade_name
            FROM learning_paths lp
            JOIN grade_skill_requirements gsr ON lp.skill_id = gsr.skill_id
            JOIN skills s ON lp.skill_id = s.skill_id
            JOIN courses c ON lp.course_id = c.course_id
            JOIN grades g ON gsr.grade_id = g.grade_id
            WHERE gsr.grade_id = %s
            ORDER BY lp.priority ASC
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (grade_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error(
                "get_learning_paths_for_grade(%s) failed: %s", grade_id, e
            )
            raise

    # ------------------------------------------------------------------
    # Certifications
    # ------------------------------------------------------------------

    def get_certification_details(self, certification_name: str) -> Optional[dict]:
        """
        Fetch full details for a certification by name.

        Args:
            certification_name: Certification name to search for.

        Returns:
            Dict with certification_id, certification_name, provider,
            or None if not found.
        """
        query = """
            SELECT
                certification_id,
                certification_name,
                provider,
                validity_years
            FROM certifications
            WHERE LOWER(certification_name) = LOWER(%s)
            LIMIT 1
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (certification_name,))
            row = cursor.fetchone()
            cursor.close()
            return row
        except mysql.connector.Error as e:
            logger.error(
                "get_certification_details(%s) failed: %s", certification_name, e
            )
            raise

    def get_certifications_for_grade(self, grade_id: int) -> list[dict]:
        """
        Fetch all certification requirements for a grade with their details.

        Args:
            grade_id: The target grade primary key.

        Returns:
            List of dicts with certification_name, provider, mandatory.
        """
        query = """
            SELECT
                c.certification_id,
                c.certification_name,
                c.provider,
                gcr.mandatory
            FROM grade_certification_requirements gcr
            JOIN certifications c ON gcr.certification_id = c.certification_id
            WHERE gcr.grade_id = %s
            ORDER BY gcr.mandatory DESC, c.certification_name
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (grade_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error(
                "get_certifications_for_grade(%s) failed: %s", grade_id, e
            )
            raise

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def get_recommended_projects(self, grade_id: int) -> list[dict]:
        """
        Fetch projects that are relevant to the target grade.

        Returns projects ordered by difficulty so the engine can
        recommend appropriately challenging work.

        Args:
            grade_id: The target grade primary key.

        Returns:
            List of dicts with project_id, project_name, technology,
            difficulty, domain.
        """
        query = """
            SELECT
                p.project_id,
                p.project_name,
                p.technology,
                p.difficulty,
                p.domain
            FROM projects p
            ORDER BY
                FIELD(p.difficulty, 'Easy', 'Medium', 'Hard'),
                p.project_name
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error(
                "get_recommended_projects(%s) failed: %s", grade_id, e
            )
            raise

    def get_all_projects(self) -> list[dict]:
        """
        Fetch all available projects as a fallback.

        Returns:
            List of all project records.
        """
        query = """
            SELECT
                p.project_id,
                p.project_name,
                p.technology,
                p.difficulty,
                p.domain
            FROM projects p
            ORDER BY FIELD(p.difficulty, 'Easy', 'Medium', 'Hard'), p.project_name
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error("get_all_projects() failed: %s", e)
            raise

    # ------------------------------------------------------------------
    # Mentors
    # ------------------------------------------------------------------

    def get_mentors_for_grade(self, target_grade_id: int) -> list[dict]:
        """
        Fetch mentors who are qualified to guide an employee
        toward the target grade.

        Args:
            target_grade_id: The target grade primary key.

        Returns:
            List of dicts with mentor_id, full_name, email,
            department, current_grade, specialisation/specialization, availability.
        """
        query = """
            SELECT
                m.mentor_id,
                e.full_name,
                e.email,
                e.department,
                g.grade_name AS current_grade,
                m.specialization AS specialisation,
                m.specialization,
                m.available AS availability,
                m.available
            FROM mentors m
            JOIN employees e ON m.employee_id = e.employee_id
            JOIN grades g ON e.current_grade_id = g.grade_id
            WHERE e.current_grade_id >= %s
              AND m.available = 1
            ORDER BY e.current_grade_id ASC, e.full_name
            LIMIT 5
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (target_grade_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error(
                "get_mentors_for_grade(%s) failed: %s", target_grade_id, e
            )
            raise

    def get_mentors_for_skill(self, skill_name: str) -> list[dict]:
        """
        Fetch mentors with expertise in a given skill area.

        Args:
            skill_name: The skill name to match against mentor specialisation.

        Returns:
            List of dicts with mentor fields.
        """
        query = """
            SELECT
                m.mentor_id,
                e.full_name,
                e.email,
                e.department,
                g.grade_name AS current_grade,
                m.specialization AS specialisation,
                m.specialization,
                m.available AS availability,
                m.available
            FROM mentors m
            JOIN employees e ON m.employee_id = e.employee_id
            JOIN grades g ON e.current_grade_id = g.grade_id
            WHERE LOWER(m.specialization) LIKE LOWER(%s)
              AND m.available = 1
            ORDER BY e.current_grade_id DESC, e.full_name
            LIMIT 3
        """
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(query, (f"%{skill_name}%",))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except mysql.connector.Error as e:
            logger.error(
                "get_mentors_for_skill(%s) failed: %s", skill_name, e
            )
            raise

    # ------------------------------------------------------------------
    # Recommendation history
    # ------------------------------------------------------------------

    def save_recommendation(
        self,
        employee_id: int,
        target_grade_id: int,
        readiness_score: float,
    ) -> None:
        """
        Persist a recommendation record to recommendation_history.

        Args:
            employee_id:     The employee the recommendation is for.
            target_grade_id: Target grade primary key ID.
            readiness_score: Calculated readiness score.
        """
        query = """
            INSERT INTO recommendation_history
                (employee_id, target_grade_id, readiness_score, recommendation_date)
            VALUES (%s, %s, %s, NOW())
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(query, (employee_id, target_grade_id, readiness_score))
            self._conn.commit()
            cursor.close()
            logger.info(
                "Recommendation saved for employee %s: target_grade=%s score=%s",
                employee_id, target_grade_id, readiness_score,
            )
        except mysql.connector.Error as e:
            logger.error(
                "save_recommendation(%s) failed: %s", employee_id, e
            )
            raise
