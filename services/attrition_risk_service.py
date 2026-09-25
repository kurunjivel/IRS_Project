"""
Phase 9 — Employee Attrition & Flight-Risk Data-Readiness & Signal Analysis Engine.

In compliance with strict ML integrity guidelines:
- Historical supervised exit/resignation labels are unavailable in the database.
- Supervised model training on fake labels is suspended.
- This service implements the Data-Readiness & Flight-Risk Signal Engine, evaluating
  organizational career stability signals while embedding explicit data readiness metadata.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from models.employee import Employee
from database.employee_repository import EmployeeRepository
from services.gap_analysis_service import GapAnalysisService
from services.readiness.readiness_engine import ReadinessEngine
from services.ml.predictor import Predictor
from config import ATTRITION_RISK_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class AttritionFactor:
    """A single factor influencing flight risk / career stability."""
    feature_name: str
    impact_type: str  # INCREASES_RISK or DECREASES_RISK
    impact_magnitude: float
    description: str


@dataclass
class AttritionRiskResult:
    """Flight-risk analysis result for an employee."""
    employee_id: int
    full_name: str
    current_grade: str
    target_grade: str
    department: str
    risk_probability: float  # 0.0 to 1.0
    risk_level: str          # LOW, MODERATE, HIGH
    model_version: str
    prediction_timestamp: str
    model_status: str        # DATA_READINESS_HEURISTIC
    data_readiness_report: str
    positive_factors: List[AttritionFactor] = field(default_factory=list)  # Decreases risk
    negative_factors: List[AttritionFactor] = field(default_factory=list)  # Increases risk
    recommended_career_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary representation."""
        return {
            "employee_id": self.employee_id,
            "full_name": self.full_name,
            "current_grade": self.current_grade,
            "target_grade": self.target_grade,
            "department": self.department,
            "risk_probability": self.risk_probability,
            "risk_level": self.risk_level,
            "model_version": self.model_version,
            "prediction_timestamp": self.prediction_timestamp,
            "model_status": self.model_status,
            "data_readiness_report": self.data_readiness_report,
            "positive_factors": [
                {
                    "feature_name": f.feature_name,
                    "impact_type": f.impact_type,
                    "impact_magnitude": f.impact_magnitude,
                    "description": f.description,
                }
                for f in self.positive_factors
            ],
            "negative_factors": [
                {
                    "feature_name": f.feature_name,
                    "impact_type": f.impact_type,
                    "impact_magnitude": f.impact_magnitude,
                    "description": f.description,
                }
                for f in self.negative_factors
            ],
            "recommended_career_actions": self.recommended_career_actions,
        }


class AttritionRiskService:
    """
    Service for calculating flight-risk signals and data readiness assessment.
    """

    DATA_READINESS_STATEMENT = (
        "Historical supervised exit/resignation labels are currently unavailable in the database. "
        "Supervised ML model training was suspended to avoid non-authentic synthetic label leakage. "
        "Flight-risk signals are computed via legitimate organizational career indicators until historical exit data is ingested."
    )

    def __init__(self, emp_repo: Optional[EmployeeRepository] = None) -> None:
        self.emp_repo = emp_repo or EmployeeRepository()
        self.gap_service = GapAnalysisService()
        self.readiness_engine = ReadinessEngine()
        self.predictor = Predictor()

    def evaluate_employee_risk(
        self,
        employee_id: int,
        gap_analysis: Optional[Dict[str, Any]] = None,
        readiness_result: Optional[Dict[str, Any]] = None,
    ) -> AttritionRiskResult:
        """
        Evaluate career stability and flight risk for an employee.

        Args:
            employee_id: Primary key of employee.
            gap_analysis: Optional precomputed gap analysis dict.
            readiness_result: Optional precomputed readiness result dict.

        Returns:
            AttritionRiskResult object.
        """
        # Load gap analysis & readiness if not provided
        if gap_analysis is None:
            gap_analysis = self.gap_service.run(employee_id)

        employee: Employee = gap_analysis["employee"]

        if readiness_result is None:
            readiness_result = self.readiness_engine.calculate(gap_analysis)

        if isinstance(readiness_result, dict):
            readiness_score = float(readiness_result.get("readiness_score", 50.0))
        else:
            readiness_score = float(getattr(readiness_result, "readiness_score", 50.0))
        skill_gaps = gap_analysis.get("skill_gaps", [])
        unmet_gaps = [g for g in skill_gaps if g.get("gap", 0) > 0]
        total_gaps_count = len(skill_gaps)
        unmet_gaps_count = len(unmet_gaps)

        # ---------------------------------------------------------
        # RISK INDICATOR EVALUATION
        # ---------------------------------------------------------

        base_risk = 0.20  # Baseline low organization attrition rate
        positive_factors: List[AttritionFactor] = []
        negative_factors: List[AttritionFactor] = []
        rec_actions: List[str] = []

        # 1. Career Tenure / Grade Stagnation
        exp_years = float(employee.experience_years or 0.0)
        if exp_years > 5.0 and employee.current_grade in ["G1", "G2"]:
            risk_inc = 0.20
            base_risk += risk_inc
            negative_factors.append(
                AttritionFactor(
                    feature_name="Grade Stagnation",
                    impact_type="INCREASES_RISK",
                    impact_magnitude=risk_inc,
                    description=f"High total experience ({exp_years:.1f} yrs) relative to current grade ({employee.current_grade}).",
                )
            )
            rec_actions.append("Accelerate skill gap resolution to qualify for target grade promotion.")
        elif exp_years <= 3.0:
            risk_dec = -0.05
            base_risk += risk_dec
            positive_factors.append(
                AttritionFactor(
                    feature_name="Early Career Phase",
                    impact_type="DECREASES_RISK",
                    impact_magnitude=abs(risk_dec),
                    description="Early career tenure with room for progression.",
                )
            )

        # 2. Skill Gap Percentage & Growth Frustration
        gap_ratio = (unmet_gaps_count / total_gaps_count) if total_gaps_count > 0 else 0.0
        if gap_ratio > 0.5:
            risk_inc = 0.18
            base_risk += risk_inc
            negative_factors.append(
                AttritionFactor(
                    feature_name="High Skill Gaps",
                    impact_type="INCREASES_RISK",
                    impact_magnitude=risk_inc,
                    description=f"{unmet_gaps_count} unaddressed skill gaps ({gap_ratio*100:.0f}% of requirements).",
                )
            )
            rec_actions.append("Enroll in targeted technical learning paths to bridge critical gaps.")
        else:
            risk_dec = -0.08
            base_risk += risk_dec
            positive_factors.append(
                AttritionFactor(
                    feature_name="Strong Skill Alignment",
                    impact_type="DECREASES_RISK",
                    impact_magnitude=abs(risk_dec),
                    description="Strong alignment with current and target grade skill requirements.",
                )
            )

        # 3. High Performance vs Delayed Readiness Mismatch
        perf_rating = float(employee.performance_rating or 3.0)
        if perf_rating >= 4.0 and readiness_score < 60.0:
            risk_inc = 0.22
            base_risk += risk_inc
            negative_factors.append(
                AttritionFactor(
                    feature_name="Performance-Readiness Mismatch",
                    impact_type="INCREASES_RISK",
                    impact_magnitude=risk_inc,
                    description=f"High performance rating ({perf_rating}/5.0) but moderate promotion readiness ({readiness_score:.1f}).",
                )
            )
            rec_actions.append("Engage with a senior mentor to align performance achievements with promotion criteria.")
        elif perf_rating >= 4.0 and readiness_score >= 75.0:
            risk_dec = -0.15
            base_risk += risk_dec
            positive_factors.append(
                AttritionFactor(
                    feature_name="High Performance & High Readiness",
                    impact_type="DECREASES_RISK",
                    impact_magnitude=abs(risk_dec),
                    description=f"Consistently strong performance ({perf_rating}/5.0) and high promotion readiness ({readiness_score:.1f}).",
                )
            )

        # 4. Project Leadership & Engagement
        lead_projects = [p for p in employee.projects if getattr(p, "lead_project", False)]
        if lead_projects:
            risk_dec = -0.10
            base_risk += risk_dec
            positive_factors.append(
                AttritionFactor(
                    feature_name="Project Leadership Engagement",
                    impact_type="DECREASES_RISK",
                    impact_magnitude=abs(risk_dec),
                    description=f"Active leadership in {len(lead_projects)} major project(s).",
                )
            )
        else:
            risk_inc = 0.08
            base_risk += risk_inc
            negative_factors.append(
                AttritionFactor(
                    feature_name="Limited Project Leadership",
                    impact_type="INCREASES_RISK",
                    impact_magnitude=risk_inc,
                    description="No recorded project leadership roles in current grade.",
                )
            )
            rec_actions.append("Seek opportunities for project module leadership in upcoming deliverables.")

        # Bound risk probability between 0.05 and 0.95
        final_probability = round(max(0.05, min(0.95, base_risk)), 2)

        # Configurable Thresholds
        low_max = ATTRITION_RISK_CONFIG["thresholds"]["LOW_MAX"]
        mod_max = ATTRITION_RISK_CONFIG["thresholds"]["MODERATE_MAX"]

        if final_probability < low_max:
            risk_level = "LOW"
        elif final_probability <= mod_max:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"

        version = ATTRITION_RISK_CONFIG.get("model_version", "attrition_v1")

        return AttritionRiskResult(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            current_grade=employee.current_grade,
            target_grade=employee.target_grade,
            department=employee.department,
            risk_probability=final_probability,
            risk_level=risk_level,
            model_version=version,
            prediction_timestamp=datetime.utcnow().isoformat() + "Z",
            model_status="DATA_READINESS_HEURISTIC",
            data_readiness_report=self.DATA_READINESS_STATEMENT,
            positive_factors=positive_factors,
            negative_factors=negative_factors,
            recommended_career_actions=rec_actions,
        )

    def get_organizational_risk_distribution(self) -> Dict[str, Any]:
        """
        Compute organizational flight-risk distribution for HR Dashboard.

        Returns:
            Dict with counts for LOW, MODERATE, HIGH risk employees.
        """
        all_emps = self.emp_repo.get_all_employees()
        low_count = 0
        mod_count = 0
        high_count = 0
        evaluations: List[Dict[str, Any]] = []

        for emp in all_emps:
            try:
                res = self.evaluate_employee_risk(emp["employee_id"])
                if res.risk_level == "LOW":
                    low_count += 1
                elif res.risk_level == "MODERATE":
                    mod_count += 1
                else:
                    high_count += 1

                evaluations.append(res.to_dict())
            except Exception as e:
                logger.warning("Error evaluating attrition risk for emp %s: %s", emp["employee_id"], e)

        return {
            "total_employees": len(all_emps),
            "summary": {
                "low_risk": low_count,
                "moderate_risk": mod_count,
                "high_risk": high_count,
            },
            "evaluations": evaluations,
            "data_readiness_report": self.DATA_READINESS_STATEMENT,
        }
