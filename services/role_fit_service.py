"""
Role Fit Service — Phase 7 extension for HR Target Role candidate analysis.

Calculates Role Fit scores for candidates against a target role/grade,
distinguishing Role Fit from Promotion Readiness while reusing the core IRS engine.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from database.employee_repository import EmployeeRepository
from database.grade_repository import GradeRepository
from services.data_loader import DataLoader
from services.gap_analysis_service import GapAnalysisService, EmployeeNotFoundError, GradeNotFoundError
from services.readiness.readiness_engine import ReadinessEngine
from services.ml.feature_engineering import FeatureEngineeringService
from services.ml.predictor import Predictor

logger = logging.getLogger(__name__)


# Default Configurable Weights for Role Fit
DEFAULT_ROLE_FIT_WEIGHTS: dict[str, float] = {
    "skills": 40.0,
    "projects": 20.0,
    "experience": 15.0,
    "certifications": 15.0,
    "performance": 10.0,
}


@dataclass
class RoleFitResult:
    """Output for an employee evaluated against a target role/grade."""

    employee_id: int
    name: str
    current_grade: str
    current_grade_id: int
    target_grade: str
    target_grade_id: int
    role_fit_score: float
    readiness_score: float
    promotion_probability: float
    eligibility: str
    status: str
    breakdown: dict = field(default_factory=dict)


class RoleFitService:
    """
    Evaluates employee candidate suitability (Role Fit) and promotion readiness
    for a target role/grade.
    """

    def __init__(self, weights: Optional[dict[str, float]] = None) -> None:
        self.weights = weights or DEFAULT_ROLE_FIT_WEIGHTS
        self._readiness_engine = ReadinessEngine()
        self._feature_service = FeatureEngineeringService()
        self._predictor = Predictor()

    def analyze_employee_role_fit(
        self, employee_id: int, target_grade_id: int
    ) -> RoleFitResult:
        """
        Calculate Role Fit and Promotion Readiness for an employee against a target grade.
        """
        gap_svc = GapAnalysisService()
        loader = DataLoader()
        try:
            employee = loader.load_employee(employee_id)
            if employee is None:
                raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

            target_req = loader.load_grade_requirement(target_grade_id)
            if target_req is None:
                raise GradeNotFoundError(f"Grade requirement for grade_id={target_grade_id} not found.")

            # Run gap analysis for employee against target grade
            gap_analysis = gap_svc.run(employee_id, target_grade_id=target_grade_id)

            # Calculate readiness score using existing ReadinessEngine
            readiness_result = self._readiness_engine.calculate(gap_analysis)
            readiness_score = readiness_result.readiness_score
            b = readiness_result.breakdown

            # Derive category match percentages (0 - 100)
            skills_pct = b.skills.percentage
            cert_pct = (b.certifications.score / b.certifications.max_score * 100.0) if b.certifications.max_score > 0 else 100.0
            exp_pct = min(100.0, (b.experience.score / (0.15 * 100.0) * 100.0)) if b.experience.current_years >= b.experience.required_years else min(100.0, (b.experience.current_years / max(1.0, b.experience.required_years) * 100.0))
            proj_pct = (b.projects.score / (0.20 * 100.0) * 100.0) if b.projects.required > 0 else 100.0
            perf_pct = (b.performance.score / (0.10 * 100.0) * 100.0)

            # Calculate weighted Role Fit Score
            total_weight = sum(self.weights.values())
            role_fit_score = round(
                (
                    skills_pct * self.weights.get("skills", 40.0)
                    + cert_pct * self.weights.get("certifications", 15.0)
                    + exp_pct * self.weights.get("experience", 15.0)
                    + proj_pct * self.weights.get("projects", 20.0)
                    + perf_pct * self.weights.get("performance", 10.0)
                ) / total_weight,
                2,
            )

            # Run ML Predictor
            feature_row = self._feature_service.build_features(gap_analysis, readiness_result)
            pred_dict = self._predictor.predict(
                feature_row.to_dict(),
                employee_id=employee.employee_id,
                current_grade=employee.current_grade,
                target_grade=target_req.grade_name,
            )
            prob = pred_dict.get("promotion_probability", 0.0)

            # Determine eligibility and status
            missing_mandatory_skills = [g for g in gap_analysis.get("skill_gaps", []) if g.get("mandatory") and g.get("gap", 0) > 0]
            missing_mandatory_certs = [c for c in gap_analysis.get("certification_gaps", []) if c.get("mandatory")]

            if readiness_score >= 85.0 and len(missing_mandatory_skills) == 0 and len(missing_mandatory_certs) == 0:
                eligibility = "Eligible"
                status_str = "Ready"
            elif readiness_score >= 60.0:
                eligibility = "Conditional"
                status_str = "Almost Ready"
            else:
                eligibility = "Not Eligible"
                status_str = "Needs Improvement"

            return RoleFitResult(
                employee_id=employee.employee_id,
                name=employee.full_name,
                current_grade=employee.current_grade,
                current_grade_id=employee.current_grade_id,
                target_grade=target_req.grade_name,
                target_grade_id=target_req.grade_id,
                role_fit_score=role_fit_score,
                readiness_score=readiness_score,
                promotion_probability=round(prob, 4),
                eligibility=eligibility,
                status=status_str,
                breakdown={
                    "skills_match": round(skills_pct, 1),
                    "certifications_match": round(cert_pct, 1),
                    "experience_match": round(exp_pct, 1),
                    "projects_match": round(proj_pct, 1),
                    "performance_match": round(perf_pct, 1),
                },
            )
        finally:
            gap_svc.close()
            loader.close()

    def get_candidates_for_role(self, target_grade_id: int) -> list[RoleFitResult]:
        """
        Analyze all employees in system against target_grade_id and rank candidates by Role Fit score.
        """
        emp_repo = EmployeeRepository()
        try:
            raw_employees = emp_repo.get_all_employees()
            if not raw_employees:
                # Mock fallback list if DB table is unpopulated
                raw_employees = [
                    {"employee_id": 1, "full_name": "Aarav Sharma"},
                    {"employee_id": 2, "full_name": "Priya Nair"},
                    {"employee_id": 3, "full_name": "Ananya Iyer"},
                ]

            results = []
            for emp in raw_employees:
                emp_id = emp["employee_id"]
                try:
                    res = self.analyze_employee_role_fit(emp_id, target_grade_id)
                    results.append(res)
                except Exception as e:
                    logger.warning("Could not analyze employee %s for role %s: %s", emp_id, target_grade_id, e)

            # Rank candidates by role_fit_score descending
            results.sort(key=lambda x: x.role_fit_score, reverse=True)
            return results
        finally:
            emp_repo.close()
