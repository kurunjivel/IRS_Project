"""
Unit and integration tests for Phase 9 — Employee Attrition / Flight-Risk Signal Analysis & Data Readiness.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from models.employee import Employee
from services.attrition_risk_service import AttritionRiskService, AttritionRiskResult
from services.career_service import CareerService
from config import ATTRITION_RISK_CONFIG
from api.main import app


@pytest.fixture
def mock_stagnant_employee():
    return Employee(
        employee_id=1,
        employee_code="EMP001",
        full_name="Stagnant Emp",
        email="stagnant@example.com",
        department="Engineering",
        experience_years=6.5,
        performance_rating=4.5,
        joining_date="2019-01-15",
        current_grade="G2",
        current_grade_id=2,
        target_grade="G3",
        target_grade_id=3,
        skills=[],
        certifications=[],
        projects=[],
    )


@pytest.fixture
def mock_stable_employee():
    return Employee(
        employee_id=2,
        employee_code="EMP002",
        full_name="Stable Emp",
        email="stable@example.com",
        department="Engineering",
        experience_years=2.0,
        performance_rating=4.2,
        joining_date="2024-01-15",
        current_grade="G2",
        current_grade_id=2,
        target_grade="G3",
        target_grade_id=3,
        skills=[],
        certifications=[],
        projects=[MagicMock(lead_project=True)],
    )


class TestAttritionRiskService:

    @patch("services.attrition_risk_service.GapAnalysisService")
    @patch("services.attrition_risk_service.ReadinessEngine")
    def test_evaluate_stagnant_employee_risk(
        self, mock_readiness_cls, mock_gap_cls, mock_stagnant_employee
    ):
        mock_gap_svc = MagicMock()
        mock_gap_svc.run.return_value = {
            "employee": mock_stagnant_employee,
            "skill_gaps": [
                {"skill": "SkillA", "gap": 2},
                {"skill": "SkillB", "gap": 3},
                {"skill": "SkillC", "gap": 1},
            ],
        }
        mock_gap_cls.return_value = mock_gap_svc

        mock_readiness_engine = MagicMock()
        mock_readiness_engine.calculate.return_value = {"readiness_score": 52.0}
        mock_readiness_cls.return_value = mock_readiness_engine

        svc = AttritionRiskService()
        result = svc.evaluate_employee_risk(1)

        # Assertions
        assert result.employee_id == 1
        assert result.model_status == "DATA_READINESS_HEURISTIC"
        assert "Historical supervised exit/resignation labels are currently unavailable" in result.data_readiness_report
        assert result.risk_level in ["MODERATE", "HIGH"]
        assert result.risk_probability > 0.40
        assert len(result.negative_factors) >= 1

    @patch("services.attrition_risk_service.GapAnalysisService")
    @patch("services.attrition_risk_service.ReadinessEngine")
    def test_evaluate_stable_employee_risk(
        self, mock_readiness_cls, mock_gap_cls, mock_stable_employee
    ):
        mock_gap_svc = MagicMock()
        mock_gap_svc.run.return_value = {
            "employee": mock_stable_employee,
            "skill_gaps": [
                {"skill": "SkillA", "gap": 0},
                {"skill": "SkillB", "gap": 0},
            ],
        }
        mock_gap_cls.return_value = mock_gap_svc

        mock_readiness_engine = MagicMock()
        mock_readiness_engine.calculate.return_value = {"readiness_score": 82.0}
        mock_readiness_cls.return_value = mock_readiness_engine

        svc = AttritionRiskService()
        result = svc.evaluate_employee_risk(2)

        # Assertions
        assert result.risk_level == "LOW"
        assert result.risk_probability < ATTRITION_RISK_CONFIG["thresholds"]["LOW_MAX"]
        assert len(result.positive_factors) >= 1

    @patch("services.attrition_risk_service.EmployeeRepository")
    @patch("services.attrition_risk_service.GapAnalysisService")
    def test_get_organizational_risk_distribution(self, mock_gap_cls, mock_emp_repo_cls):
        mock_emp_repo = MagicMock()
        mock_emp_repo.get_all_employees.return_value = [
            {"employee_id": 1},
            {"employee_id": 2},
        ]
        mock_emp_repo_cls.return_value = mock_emp_repo

        svc = AttritionRiskService(emp_repo=mock_emp_repo)
        with patch.object(svc, "evaluate_employee_risk") as mock_eval:
            mock_eval.side_effect = [
                AttritionRiskResult(
                    employee_id=1, full_name="Emp1", current_grade="G2", target_grade="G3",
                    department="Eng", risk_probability=0.20, risk_level="LOW",
                    model_version="attrition_v1", prediction_timestamp="", model_status="DATA_READINESS_HEURISTIC",
                    data_readiness_report="",
                ),
                AttritionRiskResult(
                    employee_id=2, full_name="Emp2", current_grade="G2", target_grade="G3",
                    department="Eng", risk_probability=0.72, risk_level="HIGH",
                    model_version="attrition_v1", prediction_timestamp="", model_status="DATA_READINESS_HEURISTIC",
                    data_readiness_report="",
                ),
            ]

            dist = svc.get_organizational_risk_distribution()
            assert dist["total_employees"] == 2
            assert dist["summary"]["low_risk"] == 1
            assert dist["summary"]["high_risk"] == 1


class TestAttritionRiskAPI:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch("api.routes.attrition_risk.CareerService")
    def test_get_my_attrition_risk_api(self, mock_career_svc_cls, client):
        from api.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {
            "username": "employee1", "role": "EMPLOYEE", "employee_id": 1
        }
        try:
            mock_svc = MagicMock()
            mock_svc.get_attrition_risk.return_value = {
                "employee_id": 1,
                "risk_probability": 0.25,
                "risk_level": "LOW",
                "model_version": "attrition_data_readiness_v1",
                "model_status": "DATA_READINESS_HEURISTIC",
                "data_readiness_report": "Historical supervised exit/resignation labels are currently unavailable",
                "positive_factors": [],
                "negative_factors": [],
                "recommended_career_actions": [],
            }
            mock_career_svc_cls.return_value = mock_svc

            response = client.get("/employee/me/attrition-risk")
            assert response.status_code == 200
            data = response.json()
            assert data["employee_id"] == 1
            assert data["risk_level"] == "LOW"
            assert data["model_status"] == "DATA_READINESS_HEURISTIC"
        finally:
            app.dependency_overrides.clear()

    @patch("api.routes.attrition_risk.CareerService")
    def test_get_hr_attrition_distribution_api(self, mock_career_svc_cls, client):
        from api.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {
            "username": "hr1", "role": "HR", "employee_id": 99
        }
        try:
            mock_svc = MagicMock()
            mock_svc.get_organizational_attrition_risk.return_value = {
                "total_employees": 10,
                "summary": {"low_risk": 7, "moderate_risk": 2, "high_risk": 1},
            }
            mock_career_svc_cls.return_value = mock_svc

            response = client.get("/hr/analytics/attrition-distribution")
            assert response.status_code == 200
            data = response.json()
            assert data["total_employees"] == 10
            assert data["summary"]["low_risk"] == 7
        finally:
            app.dependency_overrides.clear()
