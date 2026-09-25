"""
Succession Service — Phase 1 Enhancement 5.

Implements HR 9-Box Succession Planning Matrix by mapping employee performance ratings (X-axis)
and readiness scores (Y-axis) into a 3x3 strategic talent matrix.
"""

import logging
from typing import Optional
from database.employee_repository import EmployeeRepository
from services.data_loader import DataLoader
from services.gap_analysis_service import GapAnalysisService
from services.readiness.readiness_engine import ReadinessEngine
from services.ml.feature_engineering import FeatureEngineeringService
from services.ml.predictor import Predictor

logger = logging.getLogger(__name__)

# 9-Box Category Matrix Definitions
NINE_BOX_DEFINITIONS = {
    "HIGH_HIGH": {
        "box_id": "HIGH_HIGH",
        "title": "Immediate Successor / HiPo",
        "performance_level": "High",
        "readiness_level": "High",
        "color": "emerald",
        "description": "High performance & high readiness. Ready for immediate promotion.",
        "indicator": "READY_NOW",
    },
    "HIGH_MEDIUM": {
        "box_id": "HIGH_MEDIUM",
        "title": "Emerging Talent / High Potential",
        "performance_level": "High",
        "readiness_level": "Medium",
        "color": "teal",
        "description": "Strong performer, needs targeted skill development to achieve full promotion readiness.",
        "indicator": "READY_SOON",
    },
    "HIGH_LOW": {
        "box_id": "HIGH_LOW",
        "title": "Enigma / Development Required",
        "performance_level": "High",
        "readiness_level": "Low",
        "color": "amber",
        "description": "Top performer in current role but has significant readiness gaps for target grade.",
        "indicator": "DEVELOPMENT_REQUIRED",
    },
    "MEDIUM_HIGH": {
        "box_id": "MEDIUM_HIGH",
        "title": "Potential Successor",
        "performance_level": "Medium",
        "readiness_level": "High",
        "color": "blue",
        "description": "High technical readiness with steady performance.",
        "indicator": "READY_NOW",
    },
    "MEDIUM_MEDIUM": {
        "box_id": "MEDIUM_MEDIUM",
        "title": "Core Key Player",
        "performance_level": "Medium",
        "readiness_level": "Medium",
        "color": "slate",
        "description": "Consistently reliable performer with moderate promotion readiness.",
        "indicator": "READY_SOON",
    },
    "MEDIUM_LOW": {
        "box_id": "MEDIUM_LOW",
        "title": "Dilemma / Skill Gap",
        "performance_level": "Medium",
        "readiness_level": "Low",
        "color": "orange",
        "description": "Solid baseline worker needing structured learning pathways.",
        "indicator": "DEVELOPMENT_REQUIRED",
    },
    "LOW_HIGH": {
        "box_id": "LOW_HIGH",
        "title": "Effective Specialist / Bottleneck",
        "performance_level": "Low",
        "readiness_level": "High",
        "color": "indigo",
        "description": "High domain skills but performance needs alignment. High bottleneck risk.",
        "indicator": "TALENT_BOTTLENECK",
    },
    "LOW_MEDIUM": {
        "box_id": "LOW_MEDIUM",
        "title": "Effective Professional",
        "performance_level": "Low",
        "readiness_level": "Medium",
        "color": "purple",
        "description": "Moderate potential requiring coaching and clear performance goals.",
        "indicator": "READY_SOON",
    },
    "LOW_LOW": {
        "box_id": "LOW_LOW",
        "title": "Underperformer / Risk",
        "performance_level": "Low",
        "readiness_level": "Low",
        "color": "rose",
        "description": "Low performance and low readiness. Requires immediate PIP or role realignment.",
        "indicator": "DEVELOPMENT_REQUIRED",
    },
}


class SuccessionService:
    """Service orchestrating 9-Box talent evaluation and succession pipeline analytics."""

    def __init__(
        self,
        loader: Optional[DataLoader] = None,
        gap_svc: Optional[GapAnalysisService] = None,
        readiness_engine: Optional[ReadinessEngine] = None,
    ) -> None:
        self._loader = loader or DataLoader()
        self._gap_svc = gap_svc or GapAnalysisService()
        self._readiness_engine = readiness_engine or ReadinessEngine()

    def close(self) -> None:
        if hasattr(self._loader, "close"):
            self._loader.close()
        if hasattr(self._gap_svc, "close"):
            self._gap_svc.close()

    @staticmethod
    def classify_performance(perf_rating: float) -> str:
        """Classify performance rating into High, Medium, or Low."""
        if perf_rating >= 4.0:
            return "HIGH"
        elif perf_rating >= 3.0:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def classify_readiness(readiness_score: float) -> str:
        """Classify readiness score into High, Medium, or Low."""
        if readiness_score >= 80.0:
            return "HIGH"
        elif readiness_score >= 60.0:
            return "MEDIUM"
        return "LOW"

    def get_nine_box_matrix(
        self,
        department: Optional[str] = None,
        current_grade: Optional[str] = None,
        target_grade: Optional[str] = None,
        manager_id: Optional[int] = None,
    ) -> dict:
        """
        Generate HR 9-Box Succession Matrix with filter support.
        """
        emp_repo = EmployeeRepository()
        try:
            raw_employees = emp_repo.get_all_employees()
            if not raw_employees:
                raw_employees = [
                    {"employee_id": 1, "full_name": "Aarav Sharma"},
                    {"employee_id": 2, "full_name": "Priya Nair"},
                    {"employee_id": 3, "full_name": "Ananya Iyer"},
                ]

            # Filter employee records
            filtered_employees = []
            for r in raw_employees:
                emp = self._loader.load_employee(r["employee_id"])
                if not emp:
                    continue

                if department and emp.department.lower() != department.lower():
                    continue
                if current_grade and emp.current_grade.lower() != current_grade.lower():
                    continue
                if target_grade and emp.target_grade.lower() != target_grade.lower():
                    continue
                if manager_id is not None and getattr(emp, "manager_id", None) != manager_id:
                    continue

                filtered_employees.append(emp)

            # Initialize 9 boxes
            grid = {box_id: {**meta, "count": 0, "employees": []} for box_id, meta in NINE_BOX_DEFINITIONS.items()}
            pipeline_summary = {
                "READY_NOW": 0,
                "READY_SOON": 0,
                "DEVELOPMENT_REQUIRED": 0,
                "TALENT_BOTTLENECK": 0,
            }

            for emp in filtered_employees:
                try:
                    gap_analysis = self._gap_svc.analyze_employee_object(emp)
                    readiness_res = self._readiness_engine.calculate(gap_analysis)
                    readiness_score = readiness_res.readiness_score

                    perf_level = self.classify_performance(emp.performance_rating)
                    read_level = self.classify_readiness(readiness_score)

                    box_id = f"{perf_level}_{read_level}"
                    if box_id not in grid:
                        box_id = "MEDIUM_MEDIUM"

                    indicator = NINE_BOX_DEFINITIONS[box_id]["indicator"]
                    pipeline_summary[indicator] += 1

                    grid[box_id]["count"] += 1
                    grid[box_id]["employees"].append({
                        "employee_id": emp.employee_id,
                        "full_name": emp.full_name,
                        "email": emp.email,
                        "department": emp.department,
                        "current_grade": emp.current_grade,
                        "target_grade": emp.target_grade,
                        "performance_rating": emp.performance_rating,
                        "readiness_score": readiness_score,
                        "performance_level": perf_level,
                        "readiness_level": read_level,
                        "pipeline_indicator": indicator,
                    })
                except Exception as e:
                    logger.warning("Failed to calculate 9-box cell for employee %s: %s", emp.employee_id, e)

            total_count = len(filtered_employees)

            # Add percentage distributions
            for box_id, data in grid.items():
                data["percentage"] = round((data["count"] / max(1, total_count)) * 100, 1)

            return {
                "total_analyzed": total_count,
                "filters": {
                    "department": department,
                    "current_grade": current_grade,
                    "target_grade": target_grade,
                    "manager_id": manager_id,
                },
                "pipeline_summary": pipeline_summary,
                "grid": grid,
            }
        finally:
            emp_repo.close()
