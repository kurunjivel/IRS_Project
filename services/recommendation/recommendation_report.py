"""
Recommendation Report — IRS Phase 6.

Converts the raw output of RecommendationEngine.run() into a clean,
structured, JSON-serialisable report.

Final report schema
-------------------
{
    "employee": { ... },
    "gap_analysis": {
        "skill_gaps": [...],
        "certification_gaps": [...],
        "experience_gap": { ... },
        "project_gap": { ... },
    },
    "readiness": {
        "readiness_score": float,
        "readiness_level": str,
        "promotion_decision": str,
        "breakdown": { ... }
    },
    "prediction": {
        "promotion_probability": float,
        "prediction": str,
        "model_name": str
    },
    "recommendations": {
        "urgency": str,
        "learning": [ ... ],
        "certifications": [ ... ],
        "projects": [ ... ],
        "mentors": [ ... ],
        "summary": {
            "total": int,
            "high": int,
            "medium": int,
            "low": int
        }
    },
    "timeline": [ ... ]
}
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from models.employee import Employee
from services.recommendation.recommendation_item import (
    Priority,
    RecommendationItem,
    RecommendationType,
    TimelineMilestone,
)
from services.readiness.readiness_engine import ReadinessResult
from services.readiness.readiness_report import ReadinessReportBuilder

logger = logging.getLogger(__name__)


@dataclass
class RecommendationReport:
    """
    Fully assembled Phase 6 recommendation report.

    This is the complete combined output of all pipeline phases.
    """

    employee:            dict
    gap_analysis:        dict
    readiness:           dict
    prediction:          dict
    learning:            list[RecommendationItem]  = field(default_factory=list)
    certifications:      list[RecommendationItem]  = field(default_factory=list)
    projects:            list[RecommendationItem]  = field(default_factory=list)
    mentors:             list[RecommendationItem]  = field(default_factory=list)
    timeline:            list[TimelineMilestone]   = field(default_factory=list)
    urgency_label:       str                       = "Moderate"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def all_recommendations(self) -> list[RecommendationItem]:
        """All recommendations across all categories."""
        return self.learning + self.certifications + self.projects + self.mentors

    @property
    def high_count(self) -> int:
        return sum(1 for r in self.all_recommendations if r.priority == Priority.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for r in self.all_recommendations if r.priority == Priority.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for r in self.all_recommendations if r.priority == Priority.LOW)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a fully JSON-serialisable dict of the entire report."""
        return {
            "employee":    self.employee,
            "gap_analysis": self.gap_analysis,
            "readiness":   self.readiness,
            "prediction":  self.prediction,
            "recommendations": {
                "urgency":        self.urgency_label,
                "learning":       [r.to_dict() for r in self.learning],
                "certifications": [r.to_dict() for r in self.certifications],
                "projects":       [r.to_dict() for r in self.projects],
                "mentors":        [r.to_dict() for r in self.mentors],
                "summary": {
                    "total":  len(self.all_recommendations),
                    "high":   self.high_count,
                    "medium": self.medium_count,
                    "low":    self.low_count,
                },
            },
            "timeline": [m.to_dict() for m in self.timeline],
        }


class RecommendationReportBuilder:
    """
    Assembles a RecommendationReport from all pipeline outputs.

    Usage
    -----
    >>> builder = RecommendationReportBuilder()
    >>> report = builder.build(employee, gap_analysis,
    ...                        readiness_result, prediction, engine_result)
    >>> print(report.to_dict())
    """

    def __init__(self) -> None:
        self._readiness_builder = ReadinessReportBuilder()

    def build(
        self,
        employee: Employee,
        gap_analysis: dict,
        readiness_result: ReadinessResult,
        prediction: dict,
        engine_result: dict,
    ) -> RecommendationReport:
        """
        Build the full recommendation report.

        Args:
            employee:         The loaded Employee object.
            gap_analysis:     The dict from GapAnalysisService.run().
            readiness_result: The ReadinessResult from ReadinessEngine.calculate().
            prediction:       The dict from Predictor.predict().
            engine_result:    The dict from RecommendationEngine.run().

        Returns:
            A RecommendationReport with all fields populated.
        """
        readiness_report = self._readiness_builder.build(employee, readiness_result)

        employee_dict = {
            "employee_id":        employee.employee_id,
            "employee_code":      employee.employee_code,
            "full_name":          employee.full_name,
            "email":              employee.email,
            "department":         employee.department,
            "current_grade":      employee.current_grade,
            "target_grade":       employee.target_grade,
            "experience_years":   employee.experience_years,
            "performance_rating": employee.performance_rating,
            "joining_date":       employee.joining_date,
        }

        gap_dict = {
            "skill_gaps":          gap_analysis.get("skill_gaps", []),
            "certification_gaps":  gap_analysis.get("certification_gaps", []),
            "experience_gap":      gap_analysis.get("experience_gap", {}),
            "project_gap":         gap_analysis.get("project_gap", {}),
        }

        readiness_dict = {
            "readiness_score":    readiness_report.readiness_score,
            "readiness_level":    readiness_report.readiness_level,
            "promotion_decision": readiness_report.promotion_decision,
            "breakdown":          readiness_report.breakdown,
        }

        prediction_dict = {
            "employee_id":           prediction.get("employee_id", employee.employee_id),
            "current_grade":         prediction.get("current_grade", employee.current_grade),
            "target_grade":          prediction.get("target_grade", employee.target_grade),
            "promotion_probability": prediction.get("promotion_probability", 0.0),
            "prediction":            prediction.get("prediction", ""),
            "model_name":            prediction.get("model_name", ""),
        }

        report = RecommendationReport(
            employee=employee_dict,
            gap_analysis=gap_dict,
            readiness=readiness_dict,
            prediction=prediction_dict,
            learning=engine_result.get("learning", []),
            certifications=engine_result.get("certifications", []),
            projects=engine_result.get("projects", []),
            mentors=engine_result.get("mentors", []),
            timeline=engine_result.get("timeline", []),
            urgency_label=engine_result.get("urgency_label", "Moderate"),
        )

        logger.info(
            "RecommendationReport built for employee %s: "
            "%d total recommendations (HIGH=%d MEDIUM=%d LOW=%d), "
            "%d timeline milestones.",
            employee.employee_id,
            len(report.all_recommendations),
            report.high_count,
            report.medium_count,
            report.low_count,
            len(report.timeline),
        )
        return report
