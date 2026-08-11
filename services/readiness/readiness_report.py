"""
Readiness Report — Phase 3.

Converts a ReadinessResult into a human-readable, JSON-serialisable
report with a readiness level and promotion decision.
"""

import logging
from dataclasses import dataclass

from models.employee import Employee
from services.readiness.readiness_engine import ReadinessResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Readiness level thresholds
# ---------------------------------------------------------------------------
_LEVELS: list[tuple[float, str]] = [
    (90.0, "Promotion Ready"),
    (75.0, "Almost Ready"),
    (60.0, "Needs Improvement"),
    (40.0, "Significant Gaps"),
    (0.0,  "Not Ready"),
]

# ---------------------------------------------------------------------------
# Promotion decision thresholds
# ---------------------------------------------------------------------------
_DECISION_READY: float = 90.0
_DECISION_CONDITIONAL: float = 60.0


@dataclass
class ReadinessReport:
    """Fully resolved promotion readiness report."""

    employee: dict
    readiness_score: float
    readiness_level: str
    promotion_decision: str
    breakdown: dict


class ReadinessReportBuilder:
    """
    Converts a ReadinessResult into a structured ReadinessReport.

    Readiness levels:
        90–100  → Promotion Ready
        75–89   → Almost Ready
        60–74   → Needs Improvement
        40–59   → Significant Gaps
        0–39    → Not Ready

    Promotion decisions:
        score >= 90  → Ready
        score >= 60  → Conditional
        score <  60  → Not Ready
    """

    def build(self, employee: Employee, result: ReadinessResult) -> ReadinessReport:
        """
        Build the final readiness report.

        Args:
            employee: The loaded Employee object.
            result:   The ReadinessResult produced by ReadinessEngine.

        Returns:
            A ReadinessReport dataclass instance.
        """
        score = result.readiness_score
        level = self._resolve_level(score)
        decision = self._resolve_decision(score)

        report = ReadinessReport(
            employee=self._build_employee_dict(employee),
            readiness_score=score,
            readiness_level=level,
            promotion_decision=decision,
            breakdown=self._build_breakdown(result),
        )

        logger.info(
            "Readiness report for employee %s: score=%.2f level='%s' decision='%s'",
            employee.employee_id,
            score,
            level,
            decision,
        )
        return report

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_level(score: float) -> str:
        for threshold, label in _LEVELS:
            if score >= threshold:
                return label
        return "Not Ready"

    @staticmethod
    def _resolve_decision(score: float) -> str:
        if score >= _DECISION_READY:
            return "Ready"
        if score >= _DECISION_CONDITIONAL:
            return "Conditional"
        return "Not Ready"

    @staticmethod
    def _build_employee_dict(employee: Employee) -> dict:
        return {
            "employee_id": employee.employee_id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
            "department": employee.department,
            "current_grade": employee.current_grade,
            "target_grade": employee.target_grade,
            "experience_years": employee.experience_years,
            "performance_rating": employee.performance_rating,
        }

    @staticmethod
    def _build_breakdown(result: ReadinessResult) -> dict:
        bd = result.breakdown
        return {
            "skills": {
                "score": bd.skills.score,
                "max_score": bd.skills.max_score,
                "percentage": bd.skills.percentage,
                "missing_skills": bd.skills.missing_skills,
                "weight": bd.weights["skills"],
            },
            "certifications": {
                "score": bd.certifications.score,
                "max_score": bd.certifications.max_score,
                "completed": bd.certifications.completed,
                "missing": bd.certifications.missing,
                "weight": bd.weights["certifications"],
            },
            "experience": {
                "score": bd.experience.score,
                "current_years": bd.experience.current_years,
                "required_years": bd.experience.required_years,
                "gap_years": bd.experience.gap_years,
                "weight": bd.weights["experience"],
            },
            "projects": {
                "score": bd.projects.score,
                "completed": bd.projects.completed,
                "required": bd.projects.required,
                "remaining": bd.projects.remaining,
                "lead_completed": bd.projects.lead_completed,
                "lead_required": bd.projects.lead_required,
                "lead_remaining": bd.projects.lead_remaining,
                "weight": bd.weights["projects"],
            },
            "performance": {
                "score": bd.performance.score,
                "performance_rating": bd.performance.performance_rating,
                "weight": bd.weights["performance"],
            },
        }
