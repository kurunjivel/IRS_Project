"""
Mentor Recommendation Service — IRS Phase 6.

Matches employees to suitable mentors based on:
  1. Target grade — prefer mentors who hold or exceed the target grade.
  2. Skill-area specialisation — prefer mentors whose specialisation
     overlaps with the employee's most critical skill gaps.
  3. Department affinity — prefer mentors from the same department.

Priority rules
--------------
- Mentor matching the grade + mandatory skill area → HIGH
- Mentor matching only the grade                   → MEDIUM
- All other available mentors                      → LOW
"""

from __future__ import annotations

import logging

from models.employee import Employee
from services.recommendation.recommendation_item import (
    Priority,
    RecommendationItem,
    RecommendationType,
)

logger = logging.getLogger(__name__)

# Maximum number of mentor recommendations to produce
_MAX_MENTORS: int = 3


class MentorService:
    """
    Generates mentorship recommendations.

    Stateless — no mutable instance state.
    """

    def recommend(
        self,
        employee: Employee,
        skill_gaps: list[dict],
        grade_mentors: list[dict],
        skill_mentors: list[dict],
    ) -> list[RecommendationItem]:
        """
        Build mentor recommendations.

        Args:
            employee:      The loaded Employee object (Phase 2 input).
            skill_gaps:    Skill gaps from Phase 2 — used to identify
                           the most critical skill area for mentor matching.
            grade_mentors: Mentors for the target grade from the repository.
                           Each dict has: mentor_id, full_name, email,
                           department, current_grade, specialisation, availability.
            skill_mentors: Mentors matched on skill specialisation.
                           Same structure as grade_mentors.

        Returns:
            Ordered list of RecommendationItems (up to _MAX_MENTORS).
        """
        # Combine and deduplicate by mentor_id
        all_mentors: dict[int, dict] = {}
        for m in grade_mentors + skill_mentors:
            mid = m.get("mentor_id")
            if mid is not None and mid not in all_mentors:
                all_mentors[mid] = m

        # Mandatory skill names — for specialisation matching
        mandatory_skills = {
            g["skill"].lower()
            for g in skill_gaps
            if g.get("mandatory")
        }

        recommendations: list[RecommendationItem] = []
        seen_ids: set[int] = set()

        for mid, mentor in all_mentors.items():
            if mid in seen_ids:
                continue
            if len(recommendations) >= _MAX_MENTORS:
                break

            specialisation = (mentor.get("specialisation") or "").lower()
            dept_match = (
                mentor.get("department", "").lower()
                == employee.department.lower()
            )

            # Determine priority
            spec_skill_match = any(
                skill in specialisation for skill in mandatory_skills
            )
            if spec_skill_match:
                priority = Priority.HIGH
                match_reason = (
                    f"specialises in {mentor.get('specialisation', 'your skill area')} "
                    f"and holds {mentor.get('current_grade', 'a higher grade')}"
                )
            elif dept_match:
                priority = Priority.MEDIUM
                match_reason = (
                    f"works in your department ({employee.department}) "
                    f"and holds {mentor.get('current_grade', 'a higher grade')}"
                )
            else:
                priority = Priority.MEDIUM
                match_reason = (
                    f"holds {mentor.get('current_grade', 'a higher grade')} "
                    f"and is available for mentoring"
                )

            reason = (
                f"Recommended mentor {mentor.get('full_name', 'Unknown')} "
                f"({match_reason}). "
                f"A mentor can help accelerate your journey to {employee.target_grade}."
            )

            recommendations.append(RecommendationItem(
                type=RecommendationType.MENTORSHIP,
                title=f"Connect with mentor: {mentor.get('full_name', 'Unknown')}",
                reason=reason,
                priority=priority,
                provider=mentor.get("department", ""),
                duration="Ongoing",
                impact="Personalised guidance, career advice, and skill development support",
                metadata={
                    "mentor_id":      mid,
                    "full_name":      mentor.get("full_name"),
                    "email":          mentor.get("email"),
                    "department":     mentor.get("department"),
                    "current_grade":  mentor.get("current_grade"),
                    "specialisation": mentor.get("specialisation"),
                    "availability":   mentor.get("availability"),
                },
            ))
            seen_ids.add(mid)

        # If no mentors found in DB — surface a generic recommendation
        if not recommendations:
            recommendations.append(RecommendationItem(
                type=RecommendationType.MENTORSHIP,
                title="Seek a mentor for career progression",
                reason=(
                    "No specific mentors are currently available in the system "
                    "for your target grade. Consider requesting a mentor from "
                    "your HR department or seeking a senior colleague in "
                    f"{employee.department}."
                ),
                priority=Priority.MEDIUM,
                provider="HR Department",
                duration="Ongoing",
                impact="Mentorship accelerates career development and provides guidance on promotion criteria",
                metadata={},
            ))

        # Sort: HIGH → MEDIUM → LOW
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        recommendations.sort(key=lambda r: order[r.priority])

        logger.info(
            "MentorService: %d recommendation(s) generated "
            "(grade_mentors=%d, skill_mentors=%d).",
            len(recommendations), len(grade_mentors), len(skill_mentors),
        )
        return recommendations
