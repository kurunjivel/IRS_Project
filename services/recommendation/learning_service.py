"""
Learning Recommendation Service — IRS Phase 6.

Maps skill gaps (from Phase 2 gap analysis) to actionable course and
learning-path recommendations.

Priority rules
--------------
- Mandatory skill gap  → HIGH
- Non-mandatory gap    → MEDIUM
- Recommended learning path for grade → MEDIUM (if no major gaps remain)
- General upskilling   → LOW

This service does NOT touch the database directly.  It receives:
  - The skill_gaps list from GapAnalysisService.run()
  - A list of available courses (from RecommendationRepository)
  - A list of learning paths for the target grade (from RecommendationRepository)
"""

from __future__ import annotations

import logging

from services.recommendation.recommendation_item import (
    Priority,
    RecommendationItem,
    RecommendationType,
)

logger = logging.getLogger(__name__)

# Maximum number of course recommendations to produce
_MAX_COURSE_RECS: int = 8


class LearningService:
    """
    Generates learning recommendations from skill gaps.

    Stateless — can be called multiple times for different employees
    without re-instantiation.
    """

    def recommend(
        self,
        skill_gaps: list[dict],
        courses: list[dict],
        learning_paths: list[dict],
    ) -> list[RecommendationItem]:
        """
        Build learning recommendations from skill gaps + available courses.

        Args:
            skill_gaps:     The list returned by SkillGapService.analyze().
                            Each dict has: skill, category, current_level,
                            required_level, gap, mandatory.
            courses:        All available courses from the repository.
                            Each dict has: course_name, provider,
                            duration_hours, difficulty_level, skill_name.
            learning_paths: Learning paths for the target grade from the repo.
                            Each dict has: path_name, description,
                            estimated_duration_months, grade_name.

        Returns:
            Ordered list of RecommendationItems (HIGH first, then MEDIUM, LOW).
        """
        recommendations: list[RecommendationItem] = []

        # ── Step 1: Course recommendations per skill gap ──────────────────
        # Build a lookup map: lowercase skill name → list of courses
        course_map: dict[str, list[dict]] = {}
        for c in courses:
            key = c.get("skill_name", "").lower()
            course_map.setdefault(key, []).append(c)

        for gap in skill_gaps:
            skill_name: str = gap["skill"]
            mandatory: bool = gap["mandatory"]
            priority = Priority.HIGH if mandatory else Priority.MEDIUM

            matched_courses = course_map.get(skill_name.lower(), [])

            if matched_courses:
                # Recommend the most appropriate course
                # (lowest difficulty that still covers the gap)
                course = self._select_best_course(matched_courses, gap["gap"])
                hours  = course.get("duration_hours", 0)
                duration_str = f"{hours} hour{'s' if hours != 1 else ''}" if hours else ""

                impact = self._estimate_skill_impact(mandatory, gap["gap"])

                recommendations.append(RecommendationItem(
                    type=RecommendationType.LEARNING,
                    title=f"Complete: {course['course_name']}",
                    reason=(
                        f"Your '{skill_name}' skill is at level {gap['current_level']} "
                        f"but {gap['required_level']} is required for the target grade "
                        f"(gap = {gap['gap']} level{'s' if gap['gap'] > 1 else ''})."
                    ),
                    priority=priority,
                    provider=course.get("provider", ""),
                    duration=duration_str,
                    impact=impact,
                    metadata={
                        "course_id":        course.get("course_id"),
                        "skill":            skill_name,
                        "skill_gap":        gap["gap"],
                        "mandatory":        mandatory,
                        "difficulty_level": course.get("difficulty_level"),
                    },
                ))
            else:
                # No course found — still surface the gap as a self-study rec
                recommendations.append(RecommendationItem(
                    type=RecommendationType.LEARNING,
                    title=f"Develop skill: {skill_name}",
                    reason=(
                        f"No specific course is listed for '{skill_name}', "
                        f"but your level ({gap['current_level']}) is below the "
                        f"required level ({gap['required_level']}) for the target grade."
                    ),
                    priority=priority,
                    provider="Self-study / On-the-job",
                    duration="",
                    impact=self._estimate_skill_impact(mandatory, gap["gap"]),
                    metadata={
                        "skill":     skill_name,
                        "skill_gap": gap["gap"],
                        "mandatory": mandatory,
                    },
                ))

            if len(recommendations) >= _MAX_COURSE_RECS:
                break

        # ── Step 2: Learning path recommendations ─────────────────────────
        for path in learning_paths:
            months = path.get("estimated_duration_months", 0)
            duration_str = f"{months} month{'s' if months != 1 else ''}" if months else ""

            recommendations.append(RecommendationItem(
                type=RecommendationType.LEARNING,
                title=f"Enrol in learning path: {path['path_name']}",
                reason=(
                    f"This learning path is specifically designed for employees "
                    f"targeting {path.get('grade_name', 'the next grade')}. "
                    + (path.get("description", "") or "")
                ),
                priority=Priority.MEDIUM,
                provider="Internal",
                duration=duration_str,
                impact="Systematic skill coverage for grade progression",
                metadata={
                    "path_id":   path.get("path_id"),
                    "path_name": path.get("path_name"),
                },
            ))

        # ── Step 3: Sort: HIGH → MEDIUM → LOW ────────────────────────────
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        recommendations.sort(key=lambda r: order[r.priority])

        logger.info(
            "LearningService: %d recommendation(s) generated "
            "(skill_gaps=%d, courses=%d, paths=%d).",
            len(recommendations), len(skill_gaps), len(courses), len(learning_paths),
        )
        return recommendations

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_best_course(courses: list[dict], gap: int) -> dict:
        """
        Select the most appropriate course for a given skill gap level.

        A gap of 1 → prefer 'Beginner'; gap >= 3 → prefer 'Advanced'.
        Falls back to the first available course if no ideal match found.
        """
        difficulty_preference: dict[int, list[str]] = {
            1: ["Beginner", "Intermediate", "Advanced"],
            2: ["Intermediate", "Beginner", "Advanced"],
            3: ["Advanced", "Intermediate", "Beginner"],
        }
        pref = difficulty_preference.get(min(gap, 3), ["Intermediate"])

        for difficulty in pref:
            for c in courses:
                if (c.get("difficulty_level") or "").lower() == difficulty.lower():
                    return c
        return courses[0]

    @staticmethod
    def _estimate_skill_impact(mandatory: bool, gap: int) -> str:
        """Return a human-readable impact estimate for a skill gap."""
        if mandatory and gap >= 3:
            return "Critical — resolving this gap is essential for promotion eligibility"
        if mandatory:
            return "High — mandatory requirement; resolves a key eligibility gap"
        if gap >= 3:
            return "Significant improvement to readiness score"
        return "Moderate improvement to skill readiness score"
