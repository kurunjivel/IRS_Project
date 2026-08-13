"""
Tests for Authentication, RBAC Authorization, Employee Portal, and HR Dashboard endpoints.
"""

import sys
from unittest.mock import MagicMock, patch

# Stub mysql modules before imports
_mysql_stub = MagicMock()
sys.modules.setdefault("mysql", _mysql_stub)
sys.modules.setdefault("mysql.connector", _mysql_stub)
sys.modules.setdefault("mysql.connector.pooling", _mysql_stub)

import pytest
from fastapi.testclient import TestClient
from api.main import app
from models.employee import Employee, EmployeeSkill, EmployeeCertification, EmployeeProject

client = TestClient(app)


def _make_dummy_employee(employee_id: int = 1) -> Employee:
    return Employee(
        employee_id=employee_id,
        employee_code=f"EMP{employee_id:03d}",
        full_name="Aarav Sharma" if employee_id == 1 else "Priya Nair",
        email="aarav@example.com" if employee_id == 1 else "priya@example.com",
        department="Engineering",
        experience_years=4.5,
        performance_rating=4.2,
        joining_date="2022-03-15",
        current_grade="G2",
        current_grade_id=2,
        target_grade="G3",
        target_grade_id=3,
        skills=[EmployeeSkill("React", "Frontend", 3)],
        certifications=[EmployeeCertification("AWS Associate", "Amazon", "Completed", "2023-05-10", None)],
        projects=[EmployeeProject("Project X", "React", "Hard", "Web", "Lead", True, 12, 4.5)],
    )


class TestAuthentication:
    """Tests for /auth routes."""

    def test_hr_login_success(self):
        response = client.post("/auth/login", json={"username": "hr", "password": "hr123"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "HR"
        assert data["username"] == "hr"
        assert data["employee_id"] is None
        assert "access_token" in data

    def test_employee_login_success(self):
        response = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "EMPLOYEE"
        assert data["username"] == "aarav"
        assert data["employee_id"] == 1
        assert "access_token" in data

    def test_login_invalid_password(self):
        response = client.post("/auth/login", json={"username": "aarav", "password": "wrongpassword"})
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_unknown_username(self):
        response = client.post("/auth/login", json={"username": "nonexistent", "password": "password123"})
        assert response.status_code == 401

    def test_get_me_endpoint(self):
        login_res = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        token = login_res.json()["access_token"]

        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "aarav"
        assert data["role"] == "EMPLOYEE"
        assert data["employee_id"] == 1

    def test_logout_endpoint(self):
        login_res = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        token = login_res.json()["access_token"]

        response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]

    def test_register_new_user_success(self):
        response = client.post("/auth/register", json={
            "username": "newuser_test",
            "password": "newpassword123",
            "role": "EMPLOYEE",
            "employee_id": 1
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser_test"
        assert data["role"] == "EMPLOYEE"
        assert data["employee_id"] == 1
        assert "access_token" in data

    def test_new_user_can_login(self):
        # Register new user
        client.post("/auth/register", json={
            "username": "login_test_user",
            "password": "mysecretpassword",
            "role": "EMPLOYEE",
            "employee_id": 2
        })
        # Login with newly registered user
        login_res = client.post("/auth/login", json={"username": "login_test_user", "password": "mysecretpassword"})
        assert login_res.status_code == 200
        data = login_res.json()
        assert data["username"] == "login_test_user"
        assert data["role"] == "EMPLOYEE"

    def test_register_duplicate_username_fails(self):
        # Attempt to register existing user "aarav"
        response = client.post("/auth/register", json={
            "username": "aarav",
            "password": "anypassword",
            "role": "EMPLOYEE"
        })
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()



class TestRBACAuthorization:
    """Tests enforcing RBAC backend boundaries."""

    def test_unauthenticated_request_rejected(self):
        response = client.get("/employee/me")
        assert response.status_code == 401

        response = client.get("/hr/employees")
        assert response.status_code == 401

    def test_employee_cannot_access_hr_endpoints(self):
        login_res = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Employee attempting HR endpoints
        assert client.get("/hr/employees", headers=headers).status_code == 403
        assert client.get("/hr/roles", headers=headers).status_code == 403
        assert client.get("/hr/roles/3/candidates", headers=headers).status_code == 403
        assert client.get("/hr/analytics", headers=headers).status_code == 403

    def test_hr_can_access_hr_endpoints(self):
        login_res = client.post("/auth/login", json={"username": "hr", "password": "hr123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/hr/roles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data

    @patch("services.career_service.CareerService.get_employee")
    def test_employee_self_service_returns_authenticated_employee_data(self, mock_get_emp):
        mock_get_emp.return_value = _make_dummy_employee(1)

        login_res = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/employee/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == 1
        assert data["full_name"] == "Aarav Sharma"


class TestPromotionMessagingAndRoleFit:
    """Tests candidate ranking and 1st vs 3rd person promotion status."""

    @patch("services.career_service.CareerService.get_career_analysis")
    def test_employee_promotion_status_first_person(self, mock_ca):
        mock_ca.return_value = {
            "employee": {"employee_id": 1, "full_name": "Aarav Sharma", "current_grade": "G2", "target_grade": "G3"},
            "readiness": {"readiness_score": 78.23},
            "prediction": {"promotion_probability": 0.823},
            "gap_analysis": {
                "skills": [{"skill": "Docker", "gap": 2, "current_level": 1, "required_level": 3}],
                "certifications": [],
                "experience": {},
                "projects": {},
            },
        }

        login_res = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/employee/me/promotion-status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["perspective"] == "FIRST_PERSON"
        assert "You are not currently eligible" in data["headline"]
        assert "YOUR PROMOTION STATUS" in data["status_title"]

    @patch("services.career_service.CareerService.get_career_analysis")
    def test_hr_promotion_status_third_person(self, mock_ca):
        mock_ca.return_value = {
            "employee": {"employee_id": 1, "full_name": "Aarav Sharma", "current_grade": "G2", "target_grade": "G3"},
            "readiness": {"readiness_score": 78.23},
            "prediction": {"promotion_probability": 0.823},
            "gap_analysis": {
                "skills": [{"skill": "Docker", "gap": 2, "current_level": 1, "required_level": 3}],
                "certifications": [],
                "experience": {},
                "projects": {},
            },
        }

        login_res = client.post("/auth/login", json={"username": "hr", "password": "hr123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/hr/employees/1/promotion-status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["perspective"] == "THIRD_PERSON"
        assert "Aarav Sharma is not currently eligible" in data["headline"]
        assert "PROMOTION ELIGIBILITY" in data["status_title"]
