"""
Recommendation Engine — IRS Phase 6.

The central orchestrator for the hybrid recommendation system.

Pipeline
--------
Phase 2 Gap Analysis
        │
        ├──→ LearningService        (skill gaps → courses + learning paths)
        ├──→ CertificationService   (cert gaps → certification recommendations)
        ├──→ ProjectService         (project gap → project recommendations)
        └──→ MentorService          (grade + skill → mentor recommendations)
                │
                ↓
        PriorityService             (re-rank using Phase 3 readiness + Phase 5 ML)
                │
                ↓
        TimelineService             (generate career milestone timeline)
                │
                ↓
        RecommendationReport        (structured output)

The engine is database-aware (uses RecommendationRepository) but is NOT
responsible for running Gap Analysis or Readiness Scoring — it receives
those results as inputs.
"""

from __future__ import annotations

import logging
from typing import Optional

from database.recommendation_repository import RecommendationRepository
from models.employee import Employee
from models.grade_requirement import GradeRequirement
from services.recommendation.certification_service import CertificationService
from services.recommendation.learning_service import LearningService
from services.recommendation.mentor_service import MentorService
from services.recommendation.priority_service import PriorityService
from services.recommendation.project_service import ProjectService
from services.recommendation.recommendation_item import (
    Priority,
    RecommendationItem,
    RecommendationType,
    TimelineMilestone,
)
from services.recommendation.timeline_service import TimelineService

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Orchestrates the full Phase 6 recommendation pipeline.

    The engine is stateless between calls — each call to run() is
    independent.

    Parameters
    ----------
    repository : RecommendationRepository | None
        Optional pre-built repository (mainly used in tests for DI).
        If None, the engine creates its own repository instance.
    """

    def __init__(
        self,
        repository: Optional[RecommendationRepository] = None,
    ) -> None:
        self._repo              = repository
        self._learning_svc      = LearningService()
        self._certification_svc = CertificationService()
        self._project_svc       = ProjectService()
        self._mentor_svc        = MentorService()
        self._priority_svc      = PriorityService()
        self._timeline_svc      = TimelineService()

    def close(self) -> None:
        """Return database connection to the pool if owned by this engine."""
        if self._repo is not None:
            try:
                self._repo.close()
            except Exception:
                pass

    def run(
        self,
        gap_analysis: dict,
        readiness_result,
        prediction: dict,
    ) -> dict:
        """
        Execute the full recommendation pipeline and return the raw results dict.

        Args:
            gap_analysis:    Dict from GapAnalysisService.run().
                             Must contain: employee, requirement, skill_gaps,
                             certification_gaps, experience_gap, project_gap.
            readiness_result: ReadinessResult from ReadinessEngine.calculate().
            prediction:      Dict from Predictor.predict() containing at least
                             promotion_probability and prediction label.

        Returns:
            A dict with keys:
                learning, certifications, projects, mentors,
                timeline, all_recommendations, urgency_label,
                promotion_probability, readiness_score.
        """
        employee: Employee          = gap_analysis["employee"]
        requirement: GradeRequirement = gap_analysis["requirement"]
        skill_gaps: list[dict]      = gap_analysis["skill_gaps"]
        cert_gaps: list[dict]       = gap_analysis["certification_gaps"]
        project_gap: dict           = gap_analysis["project_gap"]

        readiness_score: float      = readiness_result.readiness_score
        promotion_probability: float = float(
            prediction.get("promotion_probability", 0.5)
        )

        # ── Fetch data from DB ─────────────────────────────────────────────
        repo = self._get_repo()
        courses, learning_paths, cert_details, \
            available_projects, grade_mentors, skill_mentors = \
            self._fetch_data(repo, employee, requirement, skill_gaps)

        # ── Generate per-category recommendations ─────────────────────────
        learning_recs = self._learning_svc.recommend(
            skill_gaps, courses, learning_paths
        )
        cert_recs = self._certification_svc.recommend(cert_gaps, cert_details)
        project_recs = self._project_svc.recommend(project_gap, available_projects)
        mentor_recs = self._mentor_svc.recommend(
            employee, skill_gaps, grade_mentors, skill_mentors
        )

        # ── Combine all recommendations ────────────────────────────────────
        all_recs: list[RecommendationItem] = (
            learning_recs + cert_recs + project_recs + mentor_recs
        )

        # ── Apply hybrid priority adjustment ──────────────────────────────
        all_recs = self._priority_svc.adjust(
            all_recs, readiness_score, promotion_probability
        )

        # ── Generate timeline ─────────────────────────────────────────────
        timeline = self._timeline_svc.build(
            employee, requirement, gap_analysis,
            readiness_score, promotion_probability,
        )

        # ── Urgency label ─────────────────────────────────────────────────
        urgency = self._priority_svc.get_urgency_label(
            readiness_score, promotion_probability
        )

        # ── Re-split by type for the structured report ────────────────────
        final_learning      = [r for r in all_recs if r.type == RecommendationType.LEARNING]
        final_certs         = [r for r in all_recs if r.type == RecommendationType.CERTIFICATION]
        final_projects      = [r for r in all_recs if r.type == RecommendationType.PROJECT]
        final_mentors       = [r for r in all_recs if r.type == RecommendationType.MENTORSHIP]

        logger.info(
            "RecommendationEngine: complete for employee %s. "
            "Recs: learning=%d certs=%d projects=%d mentors=%d timeline=%d urgency=%s.",
            employee.employee_id,
            len(final_learning), len(final_certs),
            len(final_projects), len(final_mentors),
            len(timeline), urgency,
        )

        return {
            "learning":             final_learning,
            "certifications":       final_certs,
            "projects":             final_projects,
            "mentors":              final_mentors,
            "timeline":             timeline,
            "all_recommendations":  all_recs,
            "urgency_label":        urgency,
            "promotion_probability": promotion_probability,
            "readiness_score":      readiness_score,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_repo(self) -> RecommendationRepository:
        """Return the existing repo or create a new one."""
        if self._repo is None:
            self._repo = RecommendationRepository()
        return self._repo

    def _fetch_data(
        self,
        repo: RecommendationRepository,
        employee: Employee,
        requirement: GradeRequirement,
        skill_gaps: list[dict],
    ) -> tuple[
        list[dict],  # courses
        list[dict],  # learning_paths
        list[dict],  # cert_details
        list[dict],  # available_projects
        list[dict],  # grade_mentors
        list[dict],  # skill_mentors
    ]:
        """Fetch all data required by the recommendation services."""
        # Courses — one query per unique gap skill (deduplicated)
        courses: list[dict] = []
        seen_skills: set[str] = set()
        for gap in skill_gaps:
            skill = gap["skill"]
            if skill.lower() not in seen_skills:
                try:
                    courses.extend(repo.get_courses_for_skill(skill))
                    seen_skills.add(skill.lower())
                except Exception as exc:
                    logger.warning(
                        "Could not fetch courses for skill '%s': %s", skill, exc
                    )

        # If no gaps (or no courses found) — load all courses as fallback
        if not courses:
            try:
                courses = repo.get_all_courses()
            except Exception as exc:
                logger.warning("Could not fetch all courses: %s", exc)

        # Learning paths for the target grade
        learning_paths: list[dict] = []
        try:
            learning_paths = repo.get_learning_paths_for_grade(requirement.grade_id)
        except Exception as exc:
            logger.warning("Could not fetch learning paths: %s", exc)

        # Certification details for the target grade
        cert_details: list[dict] = []
        try:
            cert_details = repo.get_certifications_for_grade(requirement.grade_id)
        except Exception as exc:
            logger.warning("Could not fetch cert details: %s", exc)

        # Projects — grade-scoped first, fall back to all
        available_projects: list[dict] = []
        try:
            available_projects = repo.get_recommended_projects(requirement.grade_id)
        except Exception as exc:
            logger.warning(
                "Could not fetch grade projects (grade_id=%s): %s. "
                "Falling back to all projects.",
                requirement.grade_id, exc,
            )
        if not available_projects:
            try:
                available_projects = repo.get_all_projects()
            except Exception as exc:
                logger.warning("Could not fetch all projects: %s", exc)

        # Mentors — by grade
        grade_mentors: list[dict] = []
        try:
            grade_mentors = repo.get_mentors_for_grade(requirement.grade_id)
        except Exception as exc:
            logger.warning("Could not fetch grade mentors: %s", exc)

        # Mentors — by top mandatory skill specialisation
        skill_mentors: list[dict] = []
        mandatory_skills = [g["skill"] for g in skill_gaps if g.get("mandatory")]
        if mandatory_skills:
            try:
                skill_mentors = repo.get_mentors_for_skill(mandatory_skills[0])
            except Exception as exc:
                logger.warning("Could not fetch skill mentors: %s", exc)

        return (
            courses, learning_paths, cert_details,
            available_projects, grade_mentors, skill_mentors,
        )
