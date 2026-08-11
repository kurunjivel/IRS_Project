"""
Project Recommendation Service — IRS Phase 6.

Maps project gaps (from Phase 2) and employee project history to actionable
project recommendations, including lead project opportunities.

Priority rules
--------------
- Lead project gap exists   → HIGH (lead project is typically harder to get)
- Total project gap exists  → HIGH (if no projects at all) / MEDIUM (if partial)
- No project gap            → LOW (general enrichment)
"""

from __future__ import annotations

import logging

from services.recommendation.recommendation_item import (
    Priority,
    RecommendationItem,
    RecommendationType,
)

logger = logging.getLogger(__name__)

# Maximum number of project recommendations to surface
_MAX_PROJECT_RECS: int = 5


class ProjectService:
    """
    Generates project recommendations from project gaps.

    Stateless — no mutable instance state.
    """

    def recommend(
        self,
        project_gap: dict,
        available_projects: list[dict],
    ) -> list[RecommendationItem]:
        """
        Build project recommendations from the project gap result.

        Args:
            project_gap:        The dict returned by ProjectGapService.analyze().
                                Has keys: total_projects, lead_projects,
                                required_projects, required_lead_projects,
                                remaining_projects, remaining_lead_projects.
            available_projects: Projects from the repository (grade-scoped or all).
                                Each dict has: project_name, technology,
                                difficulty, domain, description.

        Returns:
            Ordered list of RecommendationItems.
        """
        recommendations: list[RecommendationItem] = []

        remaining_total = project_gap.get("remaining_projects", 0)
        remaining_lead  = project_gap.get("remaining_lead_projects", 0)
        req_total       = project_gap.get("required_projects", 0)
        req_lead        = project_gap.get("required_lead_projects", 0)
        have_total      = project_gap.get("total_projects", 0)

        # ── Lead project gap ──────────────────────────────────────────────
        if remaining_lead > 0:
            lead_projects = [
                p for p in available_projects
                if p.get("difficulty", "").lower() in ("medium", "hard")
            ] or available_projects

            for proj in lead_projects[:remaining_lead]:
                proj_name = proj.get("project_name", "Lead-level project")
                tech = proj.get("technology", "")
                domain = proj.get("domain", "")

                recommendations.append(RecommendationItem(
                    type=RecommendationType.PROJECT,
                    title=f"Lead project: {proj_name}",
                    reason=(
                        f"You need {remaining_lead} more lead project(s) "
                        f"(required: {req_lead}, completed: {req_lead - remaining_lead}). "
                        f"Taking a leadership role demonstrates readiness for "
                        f"the target grade."
                    ),
                    priority=Priority.HIGH,
                    provider=f"{domain} — {tech}" if domain and tech else tech or domain,
                    duration=self._estimate_duration(proj.get("difficulty", "Medium")),
                    impact="Directly addresses lead project requirement — HIGH impact on project score",
                    metadata={
                        "project_id":   proj.get("project_id"),
                        "project_name": proj_name,
                        "technology":   tech,
                        "difficulty":   proj.get("difficulty"),
                        "domain":       domain,
                        "role":         "Lead",
                    },
                ))

        # ── General project gap ───────────────────────────────────────────
        if remaining_total > 0:
            # Avoid recommending the same projects already suggested as lead
            suggested_names = {r.metadata.get("project_name") for r in recommendations}
            gen_projects = [
                p for p in available_projects
                if p.get("project_name") not in suggested_names
            ]

            # Priority is HIGH if employee has NO projects, MEDIUM otherwise
            gen_priority = Priority.HIGH if have_total == 0 else Priority.MEDIUM

            for proj in gen_projects[:remaining_total]:
                proj_name = proj.get("project_name", "Project")
                tech = proj.get("technology", "")
                domain = proj.get("domain", "")

                recommendations.append(RecommendationItem(
                    type=RecommendationType.PROJECT,
                    title=f"Complete project: {proj_name}",
                    reason=(
                        f"You need {remaining_total} more project(s) "
                        f"(required: {req_total}, completed: {have_total}). "
                        f"Completing relevant projects builds domain experience."
                    ),
                    priority=gen_priority,
                    provider=f"{domain} — {tech}" if domain and tech else tech or domain,
                    duration=self._estimate_duration(proj.get("difficulty", "Medium")),
                    impact="Improves project completion rate and project readiness score",
                    metadata={
                        "project_id":   proj.get("project_id"),
                        "project_name": proj_name,
                        "technology":   tech,
                        "difficulty":   proj.get("difficulty"),
                        "domain":       domain,
                        "role":         "Contributor",
                    },
                ))

                if len(recommendations) >= _MAX_PROJECT_RECS:
                    break

        # ── No gap — encourage enrichment ─────────────────────────────────
        if remaining_total == 0 and remaining_lead == 0 and available_projects:
            proj = available_projects[0]
            recommendations.append(RecommendationItem(
                type=RecommendationType.PROJECT,
                title=f"Enrichment project: {proj.get('project_name', 'Additional project')}",
                reason=(
                    "You have met all project requirements. "
                    "Additional projects strengthen your portfolio and "
                    "improve your promotion probability."
                ),
                priority=Priority.LOW,
                provider=proj.get("domain", ""),
                duration=self._estimate_duration(proj.get("difficulty", "Medium")),
                impact="Portfolio enrichment — moderate improvement to ML promotion score",
                metadata={
                    "project_id":   proj.get("project_id"),
                    "project_name": proj.get("project_name"),
                    "technology":   proj.get("technology"),
                },
            ))

        # Sort: HIGH → MEDIUM → LOW
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        recommendations.sort(key=lambda r: order[r.priority])

        logger.info(
            "ProjectService: %d recommendation(s) generated "
            "(remaining=%d, remaining_lead=%d).",
            len(recommendations), remaining_total, remaining_lead,
        )
        return recommendations

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_duration(difficulty: str) -> str:
        """Estimate project duration based on difficulty level."""
        mapping = {
            "easy":   "1–2 months",
            "medium": "3–6 months",
            "hard":   "6–12 months",
        }
        return mapping.get(difficulty.lower(), "3–6 months")
