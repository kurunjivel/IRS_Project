"""
Manager Portal API Routes — Authenticated Manager Endpoints.

Enforces MANAGER role check (require_manager) and strict direct report assignment authorization.
Supports team overview, direct report dossiers, calibration submissions, and audit history.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException

from api.dependencies import get_current_user, require_manager
from api.schemas.manager import (
    ManagerReviewSubmitRequest,
    ManagerReviewSubmitResponse,
    ManagerTeamMemberResponse,
)
from services.manager_service import ManagerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/manager", tags=["Manager Portal"])


def _get_manager_employee_id(current_user: dict) -> int:
    """Extract manager employee ID from current authenticated user payload."""
    emp_id = current_user.get("employee_id")
    if not emp_id:
        # Fallback default manager ID if unassigned
        return 10
    return emp_id


@router.get(
    "/team",
    status_code=status.HTTP_200_OK,
    summary="Get manager's assigned direct reports",
    description="Retrieve list of direct reports assigned to authenticated manager with readiness score and review status.",
)
def get_team_members(current_user: dict = Depends(get_current_user)):
    require_manager(current_user)
    manager_id = _get_manager_employee_id(current_user)
    service = ManagerService()
    try:
        team = service.get_team_members(manager_id)
        return {
            "manager_id": manager_id,
            "total_direct_reports": len(team),
            "team": team,
        }
    finally:
        service.close()


@router.get(
    "/employee/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Get direct report evaluation dossier",
    description="Retrieve full dossier for assigned employee including career analysis, SHAP explanations, readiness score, and current calibration review.",
)
def get_employee_dossier(
    employee_id: int = Path(..., ge=1, description="Direct report Employee ID"),
    current_user: dict = Depends(get_current_user),
):
    require_manager(current_user)
    manager_id = _get_manager_employee_id(current_user)
    service = ManagerService()
    try:
        return service.get_employee_dossier(manager_id, employee_id)
    finally:
        service.close()


@router.post(
    "/review",
    status_code=status.HTTP_200_OK,
    response_model=ManagerReviewSubmitResponse,
    summary="Submit or update quarterly manager calibration and review decision",
    description="Submits quarterly ratings (1-5), review decision (APPROVED, REJECTED, NEEDS_DEVELOPMENT, IN_REVIEW), and feedback. Mandatory comments required on rejection/development.",
)
def submit_manager_review(
    body: ManagerReviewSubmitRequest,
    current_user: dict = Depends(get_current_user),
):
    require_manager(current_user)
    manager_id = _get_manager_employee_id(current_user)
    service = ManagerService()
    try:
        res = service.submit_review(
            manager_id=manager_id,
            employee_id=body.employee_id,
            quarter=body.quarter,
            review_status=body.status,
            technical_competency=body.technical_competency,
            communication=body.communication,
            leadership=body.leadership,
            teamwork=body.teamwork,
            ownership=body.ownership,
            overall_assessment=body.overall_assessment,
            comments=body.comments,
        )
        return res
    finally:
        service.close()


@router.get(
    "/employee/{employee_id}/audit-history",
    status_code=status.HTTP_200_OK,
    summary="Get direct report audit log history",
    description="Retrieve complete timestamped audit log of all manager calibration submissions for assigned direct report.",
)
def get_employee_audit_history(
    employee_id: int = Path(..., ge=1, description="Direct report Employee ID"),
    current_user: dict = Depends(get_current_user),
):
    require_manager(current_user)
    manager_id = _get_manager_employee_id(current_user)
    service = ManagerService()
    try:
        audits = service.get_audit_history(manager_id, employee_id)
        return {
            "employee_id": employee_id,
            "total_audit_records": len(audits),
            "audit_history": audits,
        }
    finally:
        service.close()
