"""
Automated tests for database connection lifecycle and pool stability.

Validates that:
- borrowed pooled connections are returned to the pool after successful queries
- connections are returned to the pool even when SQL or application exceptions occur
- repeated operations across multiple repositories do not exhaust the connection pool
- CareerService and career-analysis pipeline can be called repeatedly (e.g. 20+ times) without pool exhaustion
"""

import pytest
from unittest.mock import patch, MagicMock
import mysql.connector

from database.db_connection import get_pool, get_connection
from database.employee_repository import EmployeeRepository
from database.grade_repository import GradeRepository
from database.recommendation_repository import RecommendationRepository
from database.user_repository import UserRepository
from services.career_service import CareerService
from services.role_fit_service import RoleFitService
from services.auth_service import AuthService
from fastapi.testclient import TestClient
from api.main import app


class TestDatabaseConnectionLifecycle:
    """Test suite for database connection lifecycle and pool exhaustion prevention."""

    def test_connection_returned_after_successful_query(self):
        """Verify that connection is returned to the pool after a successful query."""
        emp_repo = EmployeeRepository()
        res = emp_repo.get_employee(1)
        # Should be able to borrow a connection immediately without pool exhaustion
        conn = get_connection()
        assert conn is not None
        conn.close()

    def test_connection_returned_after_sql_exception(self):
        """Verify that connection is returned to pool even if SQL raises an exception."""
        emp_repo = EmployeeRepository()
        
        # Borrow a connection and patch its cursor to raise a mysql exception
        real_get_conn = get_connection
        def mock_get_conn():
            conn = real_get_conn()
            real_cursor = conn.cursor
            def mock_cursor(*args, **kwargs):
                cur = real_cursor(*args, **kwargs)
                cur.execute = MagicMock(side_effect=mysql.connector.Error("Simulated SQL Error"))
                return cur
            conn.cursor = mock_cursor
            return conn

        with patch("database.employee_repository.get_connection", side_effect=mock_get_conn):
            with pytest.raises(mysql.connector.Error):
                emp_repo.get_employee(1)

        # Connection MUST have been returned to pool in finally block
        # Test by borrowing connection again
        conn = get_connection()
        assert conn is not None
        conn.close()

    def test_multiple_repository_operations_do_not_exhaust_pool(self):
        """Verify that running 50 repository operations sequentially does not exhaust pool (pool size=5)."""
        emp_repo = EmployeeRepository()
        grade_repo = GradeRepository()
        rec_repo = RecommendationRepository()
        user_repo = UserRepository()

        for _ in range(50):
            emp_repo.get_employee(1)
            grade_repo.get_grade(1)
            rec_repo.get_all_courses()
            user_repo.get_user_by_username("aarav")

    def test_career_analysis_service_repeated_execution(self):
        """
        Regression test: execute CareerService.get_career_analysis 20 times sequentially.
        Before the fix, pool size of 5 would exhaust after 2-3 requests.
        """
        service = CareerService()
        for i in range(20):
            result = service.get_career_analysis(1)
            assert result is not None
            assert "employee" in result
            assert "readiness" in result
            assert "recommendations" in result

    def test_role_fit_candidate_ranking_repeated_execution(self):
        """
        Regression test: execute RoleFitService candidate analysis repeatedly.
        Iterates over all candidates and runs full gap/readiness pipelines.
        """
        role_fit_svc = RoleFitService()
        for _ in range(10):
            candidates = role_fit_svc.get_candidates_for_role(1)
            assert isinstance(candidates, list)

    def test_api_career_analysis_repeated_requests(self):
        """
        Test repeated API calls to GET /employee/me/career-analysis using TestClient.
        """
        client = TestClient(app)
        
        # Login to get bearer token
        auth_resp = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make 20 repeated GET requests to /employee/me/career-analysis
        for i in range(20):
            resp = client.get("/employee/me/career-analysis", headers=headers)
            assert resp.status_code == 200, f"Request {i+1} failed with status {resp.status_code}: {resp.text}"
            data = resp.json()
            assert "employee" in data
            assert "readiness" in data
