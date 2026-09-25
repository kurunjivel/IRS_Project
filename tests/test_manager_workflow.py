"""
Comprehensive Automated Test Suite for Manager Review & Calibration Workflow (Phase 1 Enhancement 4).

Tests:
1. Authentication & RBAC enforcement for MANAGER role.
2. Manager-Employee direct report assignment & cross-manager access isolation (403 Forbidden).
3. Calibration ratings (1-5) & mandatory comment validation on rejection/needs development.
4. Approval workflow state transitions (PENDING -> APPROVED / REJECTED / NEEDS_DEVELOPMENT).
5. HR Promotion Pool filtering (HR only sees APPROVED candidates).
6. Complete audit history log tracking.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from services.auth_service import create_token
from database.manager_repository import ManagerRepository, _MEM_REVIEWS, _MEM_AUDITS
from models.manager_review import ReviewStatus

client = TestClient(app)


def get_token(username: str, role: str, employee_id: int = None) -> dict:
    payload = {"sub": username, "username": username, "role": role}
    if employee_id:
        payload["employee_id"] = employee_id
    token = create_token(payload)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_mem_stores():
    """Reset in-memory review and audit stores before each test."""
    _MEM_REVIEWS.clear()
    _MEM_AUDITS.clear()
    # Re-initialize default pending review for Employee 1
    _MEM_REVIEWS["1_Q3-2026"] = {
        "review_id": 1,
        "employee_id": 1,
        "manager_id": 10,
        "quarter": "Q3-2026",
        "status": ReviewStatus.PENDING,
        "technical_competency": 4,
        "communication": 4,
        "leadership": 3,
        "teamwork": 5,
        "ownership": 4,
        "overall_assessment": "Solid technical performance.",
        "comments": "Pending review",
        "created_at": "2026-08-01T10:00:00",
        "updated_at": "2026-08-01T10:00:00",
    }


class TestManagerRBACAndAuthorization:
    """Test RBAC restrictions and cross-manager isolation boundaries."""

    def test_unauthenticated_access_denied(self):
        res = client.get("/manager/team")
        assert res.status_code == 401

    def test_employee_role_denied_manager_access(self):
        headers = get_token("aarav", "EMPLOYEE", employee_id=1)
        res = client.get("/manager/team", headers=headers)
        assert res.status_code == 403
        assert "Manager access required" in res.json()["detail"]

    def test_hr_role_denied_manager_access(self):
        headers = get_token("hr", "HR")
        res = client.get("/manager/team", headers=headers)
        assert res.status_code == 403

    def test_manager_access_granted_to_team(self):
        headers = get_token("manager", "MANAGER", employee_id=10)
        res = client.get("/manager/team", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["manager_id"] == 10
        assert data["total_direct_reports"] >= 1

    def test_cross_manager_access_forbidden(self):
        """Manager 20 attempting to access Manager 10's direct report (Employee 1) must return 403."""
        headers_mgr20 = get_token("manager2", "MANAGER", employee_id=20)
        res = client.get("/manager/employee/1", headers=headers_mgr20)
        assert res.status_code == 403
        assert "only access direct reports assigned to you" in res.json()["detail"]

    def test_cross_manager_review_submission_forbidden(self):
        """Manager 20 attempting to submit a review for Employee 1 must return 403."""
        headers_mgr20 = get_token("manager2", "MANAGER", employee_id=20)
        payload = {
            "employee_id": 1,
            "quarter": "Q3-2026",
            "status": "APPROVED",
            "technical_competency": 5,
            "communication": 5,
            "leadership": 5,
            "teamwork": 5,
            "ownership": 5,
        }
        res = client.post("/manager/review", json=payload, headers=headers_mgr20)
        assert res.status_code == 403


class TestManagerCalibrationWorkflow:
    """Test quarterly calibration, comment validation, and status transitions."""

    def test_valid_approval_submission(self):
        headers = get_token("manager", "MANAGER", employee_id=10)
        payload = {
            "employee_id": 1,
            "quarter": "Q3-2026",
            "status": "APPROVED",
            "technical_competency": 5,
            "communication": 4,
            "leadership": 4,
            "teamwork": 5,
            "ownership": 4,
            "overall_assessment": "Exceeds expectations in all core areas.",
            "comments": "Ready for target grade promotion.",
        }
        res = client.post("/manager/review", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["review"]["status"] == "APPROVED"
        assert data["audit"]["new_status"] == "APPROVED"

    def test_rejection_without_comment_fails_validation(self):
        """Submitting REJECTED status without mandatory comments must fail."""
        headers = get_token("manager", "MANAGER", employee_id=10)
        payload = {
            "employee_id": 1,
            "quarter": "Q3-2026",
            "status": "REJECTED",
            "technical_competency": 2,
            "communication": 3,
            "leadership": 2,
            "teamwork": 3,
            "ownership": 2,
            "comments": "",  # Empty comment
        }
        res = client.post("/manager/review", json=payload, headers=headers)
        assert res.status_code == 400
        assert "Comments are mandatory" in res.json()["detail"]

    def test_needs_development_with_comments_succeeds(self):
        headers = get_token("manager", "MANAGER", employee_id=10)
        payload = {
            "employee_id": 1,
            "quarter": "Q3-2026",
            "status": "NEEDS_DEVELOPMENT",
            "technical_competency": 3,
            "communication": 3,
            "leadership": 2,
            "teamwork": 4,
            "ownership": 3,
            "comments": "Requires additional leadership mentoring before promotion.",
        }
        res = client.post("/manager/review", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["review"]["status"] == "NEEDS_DEVELOPMENT"


class TestHRPromotionPoolFiltering:
    """Test that HR only sees candidates in promotion pool after manager approval."""

    def test_hr_candidate_pool_highlights_approval_status(self):
        headers_hr = get_token("hr", "HR")

        # By default Employee 1 is PENDING, so approved_only=True returns 0 approved candidates
        res = client.get("/hr/roles/2/candidates?approved_only=true", headers=headers_hr)
        assert res.status_code == 200
        data = res.json()
        approved_ids = [c["employee_id"] for c in data["candidates"]]
        assert 1 not in approved_ids

        # Manager approves Employee 1
        headers_mgr = get_token("manager", "MANAGER", employee_id=10)
        client.post(
            "/manager/review",
            json={
                "employee_id": 1,
                "quarter": "Q3-2026",
                "status": "APPROVED",
                "technical_competency": 5,
                "communication": 4,
                "leadership": 4,
                "teamwork": 5,
                "ownership": 5,
                "comments": "Approved for promotion",
            },
            headers=headers_mgr,
        )

        # Now Employee 1 appears in HR approved promotion pool
        res_after = client.get("/hr/roles/2/candidates?approved_only=true", headers=headers_hr)
        assert res_after.status_code == 200
        approved_ids_after = [c["employee_id"] for c in res_after.json()["candidates"]]
        assert 1 in approved_ids_after


class TestAuditHistoryTrail:
    """Test full audit log history generation for manager calibrations."""

    def test_audit_history_records_state_transitions(self):
        headers_mgr = get_token("manager", "MANAGER", employee_id=10)

        # Transition 1: APPROVED
        client.post(
            "/manager/review",
            json={
                "employee_id": 1,
                "quarter": "Q3-2026",
                "status": "APPROVED",
                "technical_competency": 4,
                "communication": 4,
                "leadership": 4,
                "teamwork": 4,
                "ownership": 4,
                "comments": "Initial approval",
            },
            headers=headers_mgr,
        )

        # Transition 2: NEEDS_DEVELOPMENT
        client.post(
            "/manager/review",
            json={
                "employee_id": 1,
                "quarter": "Q3-2026",
                "status": "NEEDS_DEVELOPMENT",
                "technical_competency": 3,
                "communication": 4,
                "leadership": 3,
                "teamwork": 4,
                "ownership": 3,
                "comments": "Need further project leadership",
            },
            headers=headers_mgr,
        )

        res = client.get("/manager/employee/1/audit-history", headers=headers_mgr)
        assert res.status_code == 200
        audits = res.json()["audit_history"]
        assert len(audits) == 2
        assert audits[0]["new_status"] in ("APPROVED", "NEEDS_DEVELOPMENT")
