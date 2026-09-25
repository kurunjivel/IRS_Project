"""
Automated Test Suite for HR 9-Box Succession Planning Matrix (Phase 1 Enhancement 5).

Tests:
1. Performance rating and readiness score classification threshold logic.
2. 9-Box grid endpoint mapping and succession pipeline indicators.
3. Multi-criteria filtering (department, current_grade, target_grade).
4. HR RBAC security enforcement (401 / 403).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from services.auth_service import create_token
from services.succession_service import SuccessionService

client = TestClient(app)


def get_token(username: str, role: str, employee_id: int = None) -> dict:
    payload = {"sub": username, "username": username, "role": role}
    if employee_id:
        payload["employee_id"] = employee_id
    token = create_token(payload)
    return {"Authorization": f"Bearer {token}"}


class TestNineBoxClassificationLogic:
    """Test performance and readiness threshold classification logic."""

    def test_performance_classification_thresholds(self):
        assert SuccessionService.classify_performance(4.5) == "HIGH"
        assert SuccessionService.classify_performance(4.0) == "HIGH"
        assert SuccessionService.classify_performance(3.9) == "MEDIUM"
        assert SuccessionService.classify_performance(3.0) == "MEDIUM"
        assert SuccessionService.classify_performance(2.9) == "LOW"
        assert SuccessionService.classify_performance(1.0) == "LOW"

    def test_readiness_classification_thresholds(self):
        assert SuccessionService.classify_readiness(90.0) == "HIGH"
        assert SuccessionService.classify_readiness(80.0) == "HIGH"
        assert SuccessionService.classify_readiness(79.9) == "MEDIUM"
        assert SuccessionService.classify_readiness(60.0) == "MEDIUM"
        assert SuccessionService.classify_readiness(59.9) == "LOW"
        assert SuccessionService.classify_readiness(30.0) == "LOW"


class TestNineBoxAPIEndpointAndRBAC:
    """Test API integration, response schema, and role security boundaries."""

    def test_unauthenticated_access_denied(self):
        res = client.get("/hr/succession/nine-box")
        assert res.status_code == 401

    def test_employee_role_access_forbidden(self):
        headers = get_token("aarav", "EMPLOYEE", employee_id=1)
        res = client.get("/hr/succession/nine-box", headers=headers)
        assert res.status_code == 403
        assert "HR access required" in res.json()["detail"]

    def test_manager_role_access_forbidden(self):
        headers = get_token("manager", "MANAGER", employee_id=10)
        res = client.get("/hr/succession/nine-box", headers=headers)
        assert res.status_code == 403
        assert "HR access required" in res.json()["detail"]

    def test_hr_role_access_granted_returns_grid(self):
        headers = get_token("hr", "HR")
        res = client.get("/hr/succession/nine-box", headers=headers)
        assert res.status_code == 200

        data = res.json()
        assert "total_analyzed" in data
        assert "pipeline_summary" in data
        assert "grid" in data

        pipeline = data["pipeline_summary"]
        assert "READY_NOW" in pipeline
        assert "READY_SOON" in pipeline
        assert "DEVELOPMENT_REQUIRED" in pipeline
        assert "TALENT_BOTTLENECK" in pipeline

        grid = data["grid"]
        assert len(grid) == 9
        assert "HIGH_HIGH" in grid
        assert grid["HIGH_HIGH"]["title"] == "Immediate Successor / HiPo"

    def test_nine_box_filtering_by_department(self):
        headers = get_token("hr", "HR")
        res = client.get("/hr/succession/nine-box?department=Engineering", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["filters"]["department"] == "Engineering"

    def test_nine_box_filtering_by_current_grade(self):
        headers = get_token("hr", "HR")
        res = client.get("/hr/succession/nine-box?current_grade=G2", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["filters"]["current_grade"] == "G2"
