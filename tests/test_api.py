"""
API Test Suite — Phase 7 FastAPI Layer.

Tests all REST endpoints, validation rules, HTTP status codes,
and error handling using FastAPI TestClient.
"""

import sys
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Stub mysql.connector before any project module is imported
# ---------------------------------------------------------------------------
_mysql_stub = MagicMock()
sys.modules.setdefault("mysql", _mysql_stub)
sys.modules.setdefault("mysql.connector", _mysql_stub)
sys.modules.setdefault("mysql.connector.pooling", _mysql_stub)

import pytest
from fastapi.testclient import TestClient
from api.main import app
from models.employee import Employee, EmployeeSkill, EmployeeCertification, EmployeeProject
from services.gap_analysis_service import EmployeeNotFoundError, GradeNotFoundError

client = TestClient(app)


def _make_dummy_employee(employee_id: int = 1) -> Employee:
    """Helper to construct a dummy Employee instance."""
    return Employee(
        employee_id=employee_id,
        employee_code=f"EMP{employee_id:03d}",
        full_name="Jane Doe",
        email="jane.doe@example.com",
        department="Engineering",
        experience_years=4.5,
        performance_rating=4.2,
        joining_date="2022-03-15",
        current_grade="G2",
        current_grade_id=2,
        target_grade="G3",
        target_grade_id=3,
        skills=[
            EmployeeSkill("Python", "Backend", 4),
            EmployeeSkill("Docker", "DevOps", 3),
        ],
        certifications=[
            EmployeeCertification("AWS Associate", "Amazon", "Completed", "2023-05-10", None),
        ],
        projects=[
            EmployeeProject("Project X", "Python", "Hard", "Fintech", "Lead", True, 8, 4.5),
        ],
    )


class TestHealthCheck:
    """Test API health endpoint."""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestEmployeeEndpoint:
    """Test GET /employee/{employee_id}."""

    @patch("services.career_service.CareerService.get_employee")
    def test_get_employee_success(self, mock_get_emp):
        mock_get_emp.return_value = _make_dummy_employee(1)
        response = client.get("/employee/1")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == 1
        assert data["full_name"] == "Jane Doe"
        assert data["email"] == "jane.doe@example.com"
        assert data["current_grade"] == "G2"
        assert len(data["skills"]) == 2
        assert len(data["certifications"]) == 1
        assert len(data["projects"]) == 1

    @patch("services.career_service.CareerService.get_employee")
    def test_get_employee_not_found(self, mock_get_emp):
        mock_get_emp.side_effect = EmployeeNotFoundError("Employee 99999 not found.")
        response = client.get("/employee/99999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["status_code"] == 404

    def test_get_employee_invalid_id_zero(self):
        response = client.get("/employee/0")
        assert response.status_code == 422

    def test_get_employee_invalid_id_string(self):
        response = client.get("/employee/abc")
        assert response.status_code == 422


class TestGapAnalysisEndpoint:
    """Test GET /gap-analysis/{employee_id}."""

    @patch("services.career_service.CareerService.get_gap_analysis")
    def test_get_gap_analysis_success(self, mock_gap):
        mock_gap.return_value = {
            "employee": {
                "employee_id": 1,
                "employee_code": "EMP001",
                "full_name": "Jane Doe",
                "department": "Engineering",
                "current_grade": "G2",
                "target_grade": "G3",
                "experience_years": 4.5,
                "performance_rating": 4.2,
            },
            "gapAnalysis": {
                "skills": [
                    {
                        "skill": "Kubernetes",
                        "category": "DevOps",
                        "current_level": 1,
                        "required_level": 3,
                        "gap": 2,
                        "mandatory": True,
                    }
                ],
                "certifications": [],
                "experience": {
                    "current_years": 4.5,
                    "required_years": 5.0,
                    "remaining_years": 0.5,
                },
                "projects": {
                    "total_projects": 1,
                    "lead_projects": 1,
                    "required_projects": 3,
                    "required_lead_projects": 1,
                    "remaining_projects": 2,
                    "remaining_lead_projects": 0,
                },
            },
        }
        response = client.get("/gap-analysis/1")
        assert response.status_code == 200
        data = response.json()
        assert "employee" in data
        assert "gapAnalysis" in data
        gap = data["gapAnalysis"]
        assert len(gap["skills"]) == 1

    @patch("services.career_service.CareerService.get_gap_analysis")
    def test_get_gap_analysis_not_found(self, mock_gap):
        mock_gap.side_effect = EmployeeNotFoundError("Employee 99999 not found.")
        response = client.get("/gap-analysis/99999")
        assert response.status_code == 404
        assert response.json()["status_code"] == 404

    def test_get_gap_analysis_invalid_id(self):
        response = client.get("/gap-analysis/-5")
        assert response.status_code == 422


class TestReadinessEndpoint:
    """Test GET /readiness/{employee_id}."""

    @patch("services.career_service.CareerService.get_readiness")
    def test_get_readiness_success(self, mock_readiness):
        mock_readiness.return_value = {
            "employee": {"employee_id": 1, "full_name": "Jane Doe"},
            "readiness_score": 85.5,
            "readiness_level": "Almost Ready",
            "promotion_decision": "Conditional",
            "breakdown": {
                "skills": {"score": 32.0, "max_score": 40.0, "percentage": 80.0, "missing_skills": ["Kubernetes"], "weight": 0.4},
                "certifications": {"score": 15.0, "max_score": 15.0, "completed": 1, "missing": [], "weight": 0.15},
                "experience": {"score": 13.5, "current_years": 4.5, "required_years": 5.0, "gap_years": 0.5, "weight": 0.15},
                "projects": {"score": 15.0, "completed": 1, "required": 3, "remaining": 2, "lead_completed": 1, "lead_required": 1, "lead_remaining": 0, "weight": 0.2},
                "performance": {"score": 10.0, "performance_rating": 4.2, "weight": 0.1},
            },
        }
        response = client.get("/readiness/1")
        assert response.status_code == 200
        data = response.json()
        assert data["readiness_score"] == 85.5
        assert data["readiness_level"] == "Almost Ready"
        assert data["promotion_decision"] == "Conditional"
        assert "breakdown" in data

    @patch("services.career_service.CareerService.get_readiness")
    def test_get_readiness_not_found(self, mock_readiness):
        mock_readiness.side_effect = EmployeeNotFoundError("Employee 99999 not found.")
        response = client.get("/readiness/99999")
        assert response.status_code == 404

    def test_get_readiness_invalid_id(self):
        response = client.get("/readiness/invalid")
        assert response.status_code == 422


class TestPredictionEndpoint:
    """Test GET /prediction/{employee_id}."""

    @patch("services.career_service.CareerService.get_prediction")
    def test_get_prediction_success(self, mock_pred):
        mock_pred.return_value = {
            "employee_id": 1,
            "current_grade": "G2",
            "target_grade": "G3",
            "promotion_probability": 0.87,
            "prediction": "Likely Progression",
            "model_name": "RandomForestClassifier",
        }
        response = client.get("/prediction/1")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == 1
        assert data["current_grade"] == "G2"
        assert data["target_grade"] == "G3"
        assert data["promotion_probability"] == 0.87
        assert data["prediction"] == "Likely Progression"
        assert data["model_name"] == "RandomForestClassifier"

    @patch("services.career_service.CareerService.get_prediction")
    def test_get_prediction_not_found(self, mock_pred):
        mock_pred.side_effect = EmployeeNotFoundError("Employee 99999 not found.")
        response = client.get("/prediction/99999")
        assert response.status_code == 404

    def test_get_prediction_invalid_id(self):
        response = client.get("/prediction/0")
        assert response.status_code == 422


class TestRecommendationsEndpoint:
    """Test GET /recommendations/{employee_id}."""

    @patch("services.career_service.CareerService.get_recommendations")
    def test_get_recommendations_success(self, mock_recs):
        mock_recs.return_value = {
            "urgency": "High",
            "learning": [
                {
                    "type": "Learning",
                    "title": "Mastering Kubernetes Architecture",
                    "reason": "Mandatory skill gap for G3",
                    "priority": "HIGH",
                    "provider": "Corporate Learning",
                    "duration": "4 weeks",
                    "impact": "High impact",
                    "metadata": {"skill": "Kubernetes"},
                }
            ],
            "certifications": [],
            "projects": [],
            "mentors": [],
            "summary": {"total": 1, "high": 1, "medium": 0, "low": 0},
            "timeline": [
                {
                    "month": 1,
                    "title": "Skill Gap Closure",
                    "description": "Complete Kubernetes training",
                    "category": "Learning",
                }
            ],
        }
        response = client.get("/recommendations/1")
        assert response.status_code == 200
        data = response.json()
        assert data["urgency"] == "High"
        assert len(data["learning"]) == 1
        assert data["summary"]["total"] == 1
        assert len(data["timeline"]) == 1

    @patch("services.career_service.CareerService.get_recommendations")
    def test_get_recommendations_not_found(self, mock_recs):
        mock_recs.side_effect = EmployeeNotFoundError("Employee 99999 not found.")
        response = client.get("/recommendations/99999")
        assert response.status_code == 404

    def test_get_recommendations_invalid_id(self):
        response = client.get("/recommendations/-1")
        assert response.status_code == 422


class TestCareerAnalysisEndpoint:
    """Test GET /career-analysis/{employee_id}."""

    @patch("services.career_service.CareerService.get_career_analysis")
    def test_get_career_analysis_success(self, mock_ca):
        mock_ca.return_value = {
            "employee": {
                "employee_id": 1,
                "full_name": "Jane Doe",
                "department": "Engineering",
                "current_grade": "G2",
                "target_grade": "G3",
            },
            "gap_analysis": {
                "skills": [],
                "certifications": [],
                "experience": {},
                "projects": {},
            },
            "readiness": {
                "readiness_score": 85.5,
                "readiness_level": "Almost Ready",
                "promotion_decision": "Conditional",
                "breakdown": {
                    "skills": {"score": 32.0, "max_score": 40.0, "percentage": 80.0, "missing_skills": [], "weight": 0.4},
                    "certifications": {"score": 15.0, "max_score": 15.0, "completed": 0, "missing": [], "weight": 0.15},
                    "experience": {"score": 13.5, "current_years": 4.5, "required_years": 5.0, "gap_years": 0.5, "weight": 0.15},
                    "projects": {"score": 15.0, "completed": 1, "required": 3, "remaining": 2, "lead_completed": 1, "lead_required": 1, "lead_remaining": 0, "weight": 0.2},
                    "performance": {"score": 10.0, "performance_rating": 4.2, "weight": 0.1},
                },
            },
            "prediction": {
                "employee_id": 1,
                "current_grade": "G2",
                "target_grade": "G3",
                "promotion_probability": 0.87,
                "prediction": "Likely Progression",
                "model_name": "RandomForestClassifier",
            },
            "recommendations": {
                "urgency": "High",
                "learning": [],
                "certifications": [],
                "projects": [],
                "mentors": [],
                "summary": {"total": 0, "high": 0, "medium": 0, "low": 0},
                "timeline": [],
            },
        }
        response = client.get("/career-analysis/1")
        assert response.status_code == 200
        data = response.json()
        assert "employee" in data
        assert "gap_analysis" in data
        assert "readiness" in data
        assert "prediction" in data
        assert "recommendations" in data

        pred = data["prediction"]
        assert pred["promotion_probability"] == 0.87
        assert pred["prediction"] == "Likely Progression"

        recs = data["recommendations"]
        assert recs["urgency"] == "High"

    @patch("services.career_service.CareerService.get_career_analysis")
    def test_get_career_analysis_not_found(self, mock_ca):
        mock_ca.side_effect = EmployeeNotFoundError("Employee 99999 not found.")
        response = client.get("/career-analysis/99999")
        assert response.status_code == 404

    def test_get_career_analysis_invalid_id(self):
        response = client.get("/career-analysis/abc")
        assert response.status_code == 422


class TestExceptionHandling:
    """Test error handling for service failures."""

    @patch("services.career_service.CareerService.get_prediction")
    def test_file_not_found_exception(self, mock_pred):
        mock_pred.side_effect = FileNotFoundError("Model file ml_models/promotion_model.pkl not found.")
        response = client.get("/prediction/1")
        assert response.status_code == 503
        data = response.json()
        assert data["status_code"] == 503
        assert "Service unavailable" in data["detail"]

    @patch("services.career_service.CareerService.get_employee")
    def test_unexpected_exception(self, mock_get_emp):
        mock_get_emp.side_effect = Exception("Unexpected database lock")
        response = client.get("/employee/1")
        assert response.status_code == 500
        data = response.json()
        assert data["status_code"] == 500
        assert "unexpected error" in data["detail"]
