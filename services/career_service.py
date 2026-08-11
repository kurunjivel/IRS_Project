"""
Career Service — Phase 7 API orchestration layer.

Encapsulates pipeline execution and domain service invocation to keep API
route handlers clean and focused strictly on HTTP concerns.
"""

from __future__ import annotations

import logging
from typing import Optional

from models.employee import Employee
from services.data_loader import DataLoader
from services.gap_analysis_service import (
    GapAnalysisService,
    EmployeeNotFoundError,
    GradeNotFoundError,
)
from services.json_builder import JsonBuilder
from services.readiness.readiness_engine import ReadinessEngine
from services.readiness.readiness_report import ReadinessReportBuilder
from services.ml.feature_engineering import FeatureEngineeringService
from services.ml.predictor import Predictor
from services.recommendation.recommendation_engine import RecommendationEngine
from services.recommendation.recommendation_report import RecommendationReportBuilder

logger = logging.getLogger(__name__)


class CareerService:
    """Orchestrates Phase 2–6 business logic for Phase 7 API endpoints."""

    def __init__(self) -> None:
        self._json_builder = JsonBuilder()
        self._readiness_engine = ReadinessEngine()
        self._readiness_report_builder = ReadinessReportBuilder()
        self._feature_service = FeatureEngineeringService()
        self._predictor = Predictor()
        self._recommendation_engine = RecommendationEngine()
        self._recommendation_report_builder = RecommendationReportBuilder()

    def get_employee(self, employee_id: int) -> Employee:
        """
        Fetch employee profile details.

        Raises:
            EmployeeNotFoundError: If employee does not exist.
        """
        loader = DataLoader()
        try:
            employee = loader.load_employee(employee_id)
            if employee is None:
                raise EmployeeNotFoundError(f"Employee {employee_id} not found.")
            return employee
        finally:
            loader.close()

    def get_gap_analysis(self, employee_id: int) -> dict:
        """
        Run gap analysis pipeline for employee.

        Returns:
            JSON-serialisable dict from JsonBuilder.
        """
        gap_svc = GapAnalysisService()
        try:
            raw_analysis = gap_svc.run(employee_id)
            return self._json_builder.build(raw_analysis)
        finally:
            gap_svc.close()

    def get_readiness(self, employee_id: int) -> dict:
        """
        Run gap analysis and calculate readiness score.

        Returns:
            Dict matching readiness report.
        """
        gap_svc = GapAnalysisService()
        try:
            raw_analysis = gap_svc.run(employee_id)
            employee = raw_analysis["employee"]
            readiness_result = self._readiness_engine.calculate(raw_analysis)
            report = self._readiness_report_builder.build(employee, readiness_result)
            return report.__dict__
        finally:
            gap_svc.close()

    def get_prediction(self, employee_id: int) -> dict:
        """
        Run gap analysis, readiness, feature extraction, and ML prediction.

        Returns:
            Prediction dict.
        """
        gap_svc = GapAnalysisService()
        try:
            raw_analysis = gap_svc.run(employee_id)
            employee = raw_analysis["employee"]
            readiness_result = self._readiness_engine.calculate(raw_analysis)
            feature_row = self._feature_service.build_features(raw_analysis, readiness_result)
            prediction = self._predictor.predict(
                feature_row.to_dict(),
                employee_id=employee.employee_id,
                current_grade=employee.current_grade,
                target_grade=employee.target_grade,
            )
            return prediction
        finally:
            gap_svc.close()

    def get_recommendations(self, employee_id: int) -> dict:
        """
        Run full recommendation engine.

        Returns:
            Structured recommendations dict (urgency, learning, certifications, projects, mentors, summary, timeline).
        """
        gap_svc = GapAnalysisService()
        try:
            raw_analysis = gap_svc.run(employee_id)
            employee = raw_analysis["employee"]
            readiness_result = self._readiness_engine.calculate(raw_analysis)
            feature_row = self._feature_service.build_features(raw_analysis, readiness_result)
            prediction = self._predictor.predict(
                feature_row.to_dict(),
                employee_id=employee.employee_id,
                current_grade=employee.current_grade,
                target_grade=employee.target_grade,
            )
            engine_result = self._recommendation_engine.run(
                raw_analysis, readiness_result, prediction
            )
            report = self._recommendation_report_builder.build(
                employee, raw_analysis, readiness_result, prediction, engine_result
            )
            report_dict = report.to_dict()
            recs_data = report_dict["recommendations"]
            recs_data["timeline"] = report_dict.get("timeline", [])
            return recs_data
        finally:
            gap_svc.close()
            self._recommendation_engine.close()

    def get_career_analysis(self, employee_id: int) -> dict:
        """
        Run end-to-end career analysis pipeline.

        Returns:
            Combined dictionary with employee, gap_analysis, readiness, prediction, recommendations.
        """
        gap_svc = GapAnalysisService()
        try:
            raw_analysis = gap_svc.run(employee_id)
            employee = raw_analysis["employee"]
            readiness_result = self._readiness_engine.calculate(raw_analysis)
            feature_row = self._feature_service.build_features(raw_analysis, readiness_result)
            prediction = self._predictor.predict(
                feature_row.to_dict(),
                employee_id=employee.employee_id,
                current_grade=employee.current_grade,
                target_grade=employee.target_grade,
            )
            engine_result = self._recommendation_engine.run(
                raw_analysis, readiness_result, prediction
            )
            report = self._recommendation_report_builder.build(
                employee, raw_analysis, readiness_result, prediction, engine_result
            )
            full_report = report.to_dict()
            recs = full_report["recommendations"]
            recs["timeline"] = full_report.get("timeline", [])
            return {
                "employee": full_report["employee"],
                "gap_analysis": full_report["gap_analysis"],
                "readiness": full_report["readiness"],
                "prediction": full_report["prediction"],
                "recommendations": recs,
            }
        finally:
            gap_svc.close()
            self._recommendation_engine.close()
