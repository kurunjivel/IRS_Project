"""
Simulation Service — Phase 1.3 What-If Career Scenario Engine.

Allows employees to simulate career improvements (skill levels, certifications, projects, experience)
in memory without modifying database state.

Reuses the exact same business logic services:
- GapAnalysisService
- ReadinessEngine
- FeatureEngineeringService
- Predictor
- SkillDecayService
"""

from __future__ import annotations

import copy
import datetime
import logging
from typing import Any, Optional

from models.employee import Employee, EmployeeSkill, EmployeeCertification, EmployeeProject
from services.data_loader import DataLoader
from services.gap_analysis_service import GapAnalysisService, EmployeeNotFoundError
from services.readiness.readiness_engine import ReadinessEngine
from services.ml.feature_engineering import FeatureEngineeringService
from services.ml.predictor import Predictor
from services.skill_decay_service import SkillDecayService
from api.schemas.simulation import SimulationRequest

logger = logging.getLogger(__name__)


def _classify_readiness_level(score: float) -> str:
    """Classify readiness level based on composite score."""
    if score >= 80.0:
        return "Ready for Promotion"
    elif score >= 60.0:
        return "Needs Development"
    else:
        return "Under Evaluation"


class SimulationService:
    """Orchestrates in-memory What-If career scenario simulations."""

    def __init__(self) -> None:
        self._decay_service = SkillDecayService()
        self._readiness_engine = ReadinessEngine()
        self._feature_service = FeatureEngineeringService()
        self._predictor = Predictor()

    def simulate(self, request: SimulationRequest) -> dict:
        """
        Run What-If scenario evaluation against baseline employee profile.

        Args:
            request: SimulationRequest containing simulated feature overrides.

        Returns:
            Dict matching SimulationResponse schema.
        """
        loader = DataLoader()
        gap_svc = GapAnalysisService()

        try:
            emp_id = request.employee_id if request.employee_id is not None else 1
            employee = loader.load_employee(emp_id)
            if employee is None:
                raise EmployeeNotFoundError(f"Employee {emp_id} not found.")

            # 1. Clone employee for isolated simulation
            sim_employee = copy.deepcopy(employee)
            today_str = str(datetime.date.today())

            # 2. Apply Skill Overrides
            for s_override in request.skills:
                match_skill = next(
                    (sk for sk in sim_employee.skills if sk.skill_name.lower() == s_override.skill_name.lower()),
                    None
                )
                if match_skill:
                    match_skill.skill_level = s_override.simulated_level
                    match_skill.last_used_date = today_str
                else:
                    new_sk = EmployeeSkill(
                        skill_name=s_override.skill_name,
                        category="Simulated",
                        skill_level=s_override.simulated_level,
                        last_used_date=today_str,
                    )
                    sim_employee.skills.append(new_sk)

            # 3. Apply Certification Overrides
            for c_override in request.certifications:
                if not c_override.completed:
                    continue
                match_cert = next(
                    (c for c in sim_employee.certifications if c.certification_name.lower() == c_override.certification_name.lower()),
                    None
                )
                if match_cert:
                    match_cert.status = "Completed"
                    match_cert.completion_date = today_str
                else:
                    new_cert = EmployeeCertification(
                        certification_name=c_override.certification_name,
                        provider="Simulated",
                        status="Completed",
                        completion_date=today_str,
                        expiry_date=None,
                    )
                    sim_employee.certifications.append(new_cert)

            # 4. Apply Project Overrides
            if request.projects:
                for i in range(request.projects.additional_projects):
                    is_lead = (i < request.projects.additional_lead_projects)
                    sim_employee.projects.append(
                        EmployeeProject(
                            project_name=f"Simulated Project {i + 1}",
                            technology="Python, Cloud",
                            difficulty="Medium",
                            domain="Engineering",
                            role="Project Lead" if is_lead else "Contributor",
                            lead_project=is_lead,
                            duration_months=6,
                            project_rating=4.5,
                        )
                    )

            # 5. Apply Experience Overrides
            if request.experience and request.experience.additional_experience_years > 0:
                sim_employee.experience_years += request.experience.additional_experience_years

            # Apply decay recency logic to simulated employee
            self._decay_service.apply_decay_to_employee(sim_employee)

            # 6. Run Baseline Pipeline
            baseline_raw = gap_svc.analyze_employee_object(employee, request.target_grade_id)
            baseline_readiness = self._readiness_engine.calculate(baseline_raw)
            baseline_features = self._feature_service.build_features(baseline_raw, baseline_readiness)
            baseline_pred = self._predictor.predict(
                baseline_features.to_dict(),
                employee_id=employee.employee_id,
                current_grade=employee.current_grade,
                target_grade=employee.target_grade,
            )

            # 7. Run Simulated Pipeline (Exact same engines!)
            sim_raw = gap_svc.analyze_employee_object(sim_employee, request.target_grade_id)
            sim_readiness = self._readiness_engine.calculate(sim_raw)
            sim_features = self._feature_service.build_features(sim_raw, sim_readiness)
            sim_pred = self._predictor.predict(
                sim_features.to_dict(),
                employee_id=sim_employee.employee_id,
                current_grade=sim_employee.current_grade,
                target_grade=sim_employee.target_grade,
            )

            # 8. Compute Resolved Gaps
            resolved_skill_gaps = []
            base_skill_gaps = baseline_raw.get("skill_gaps", [])
            sim_skill_map = {g["skill"].lower(): g for g in sim_raw.get("skill_gaps", [])}

            for b_gap in base_skill_gaps:
                s_name = b_gap["skill"].lower()
                s_gap = sim_skill_map.get(s_name)
                if s_gap is None or s_gap.get("gap", 0) < b_gap.get("gap", 0):
                    resolved_skill_gaps.append(b_gap["skill"])

            resolved_certs = []
            base_cert_gaps = baseline_raw.get("certification_gaps", [])
            sim_cert_names = {c["certification"].lower() for c in sim_raw.get("certification_gaps", [])}
            for b_cert in base_cert_gaps:
                c_title = b_cert["certification"]
                if c_title.lower() not in sim_cert_names:
                    resolved_certs.append(c_title)

            # Also add requested certs that were simulated as completed
            for c in request.certifications:
                if c.completed and c.certification_name not in resolved_certs:
                    resolved_certs.append(c.certification_name)

            readiness_diff = round(sim_readiness.readiness_score - baseline_readiness.readiness_score, 2)
            prob_diff = round(sim_pred["promotion_probability"] - baseline_pred["promotion_probability"], 4)

            shap_summary = None
            if sim_pred.get("shap_analysis"):
                shap_summary = sim_pred["shap_analysis"].get("summary")

            baseline_level = _classify_readiness_level(baseline_readiness.readiness_score)
            sim_level = _classify_readiness_level(sim_readiness.readiness_score)

            return {
                "employee_id": employee.employee_id,
                "employee_name": employee.full_name,
                "current_grade": employee.current_grade,
                "target_grade": employee.target_grade,
                "baseline_readiness_score": baseline_readiness.readiness_score,
                "simulated_readiness_score": sim_readiness.readiness_score,
                "readiness_score_diff": readiness_diff,
                "baseline_promotion_probability": baseline_pred["promotion_probability"],
                "simulated_promotion_probability": sim_pred["promotion_probability"],
                "probability_diff": prob_diff,
                "baseline_readiness_level": baseline_level,
                "simulated_readiness_level": sim_level,
                "baseline_prediction": baseline_pred["prediction"],
                "simulated_prediction": sim_pred["prediction"],
                "resolved_skill_gaps": resolved_skill_gaps,
                "resolved_certifications": resolved_certs,
                "simulated_shap_summary": shap_summary,
            }
        finally:
            loader.close()
            gap_svc.close()
