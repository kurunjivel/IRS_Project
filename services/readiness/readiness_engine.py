"""
Readiness Engine — Phase 3.

Orchestrates all scoring services and combines their results into
a single readiness score and breakdown dictionary.
"""

import logging
from dataclasses import dataclass, field

from models.employee import Employee
from models.grade_requirement import GradeRequirement
from services.readiness.skill_score_service import SkillScoreService, SkillScoreResult
from services.readiness.certification_score_service import (
    CertificationScoreService,
    CertificationScoreResult,
)
from services.readiness.experience_score_service import (
    ExperienceScoreService,
    ExperienceScoreResult,
)
from services.readiness.project_score_service import ProjectScoreService, ProjectScoreResult
from services.readiness.performance_score_service import (
    PerformanceScoreService,
    PerformanceScoreResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights (must sum to 100)
# ---------------------------------------------------------------------------
WEIGHT_SKILLS: float = 40.0
WEIGHT_PROJECTS: float = 20.0
WEIGHT_EXPERIENCE: float = 15.0
WEIGHT_CERTIFICATIONS: float = 15.0
WEIGHT_PERFORMANCE: float = 10.0


@dataclass
class ReadinessBreakdown:
    """Detailed per-category scoring breakdown."""

    skills: SkillScoreResult
    certifications: CertificationScoreResult
    experience: ExperienceScoreResult
    projects: ProjectScoreResult
    performance: PerformanceScoreResult
    weights: dict[str, float] = field(default_factory=lambda: {
        "skills": WEIGHT_SKILLS,
        "projects": WEIGHT_PROJECTS,
        "experience": WEIGHT_EXPERIENCE,
        "certifications": WEIGHT_CERTIFICATIONS,
        "performance": WEIGHT_PERFORMANCE,
    })


@dataclass
class ReadinessResult:
    """Combined output of the readiness engine."""

    readiness_score: float
    breakdown: ReadinessBreakdown


class ReadinessEngine:
    """
    Combines all scoring services to produce an overall readiness score.

    Receives the raw gap analysis output from Phase 2 — does not touch
    the database or any repository layer.
    """

    def __init__(self) -> None:
        self._skill_svc = SkillScoreService()
        self._cert_svc = CertificationScoreService()
        self._exp_svc = ExperienceScoreService()
        self._proj_svc = ProjectScoreService()
        self._perf_svc = PerformanceScoreService()

    def calculate(self, gap_analysis: dict) -> ReadinessResult:
        """
        Calculate the overall promotion readiness score.

        Args:
            gap_analysis: The dict returned by GapAnalysisService.run() containing:
                          employee, requirement, skill_gaps, certification_gaps,
                          experience_gap, project_gap.

        Returns:
            ReadinessResult with the overall score and full breakdown.
        """
        employee: Employee = gap_analysis["employee"]
        requirement: GradeRequirement = gap_analysis["requirement"]

        skill_result = self._skill_svc.calculate(
            employee, requirement, gap_analysis["skill_gaps"]
        )
        cert_result = self._cert_svc.calculate(
            employee, requirement, gap_analysis["certification_gaps"]
        )
        exp_result = self._exp_svc.calculate(employee, gap_analysis["experience_gap"])
        proj_result = self._proj_svc.calculate(employee, gap_analysis["project_gap"])
        perf_result = self._perf_svc.calculate(employee)

        readiness_score = round(
            skill_result.score
            + cert_result.score
            + exp_result.score
            + proj_result.score
            + perf_result.score,
            2,
        )

        logger.info(
            "Readiness score for employee %s: %.2f / 100",
            employee.employee_id,
            readiness_score,
        )

        return ReadinessResult(
            readiness_score=readiness_score,
            breakdown=ReadinessBreakdown(
                skills=skill_result,
                certifications=cert_result,
                experience=exp_result,
                projects=proj_result,
                performance=perf_result,
            ),
        )
