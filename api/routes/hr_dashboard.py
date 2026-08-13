"""
HR Dashboard API routes — Authenticated HR Administration Endpoints.

Enforces HR-only access for target role selection, candidate ranking, employee analysis,
and organization-wide analytics.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException

from api.dependencies import get_current_user, require_hr
from database.employee_repository import EmployeeRepository
from database.grade_repository import GradeRepository
from services.career_service import CareerService
from services.role_fit_service import RoleFitService
from services.promotion_messaging_service import build_hr_promotion_status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/hr", tags=["HR Dashboard"])


@router.get(
    "/employees",
    status_code=status.HTTP_200_OK,
    summary="List all employees",
    description="Retrieve listing of all active employees for HR dashboard.",
)
def list_employees(current_user: dict = Depends(get_current_user)):
    require_hr(current_user)
    repo = EmployeeRepository()
    try:
        employees = repo.get_all_employees()
        return {"total": len(employees), "employees": employees}
    finally:
        repo.close()


@router.get(
    "/roles",
    status_code=status.HTTP_200_OK,
    summary="List available target roles/grades",
    description="Fetch available target roles/grades loaded dynamically from the database.",
)
def list_roles(current_user: dict = Depends(get_current_user)):
    require_hr(current_user)
    repo = GradeRepository()
    try:
        grades = repo.get_all_grades()
        return {"total": len(grades), "roles": grades}
    finally:
        repo.close()


@router.get(
    "/roles/{role_id}/candidates",
    status_code=status.HTTP_200_OK,
    summary="Analyze and rank candidate employees for a target role/grade",
    description="Runs Role Fit analysis for all eligible employees against selected target role and ranks them by Role Fit Score.",
)
def get_role_candidates(
    role_id: int = Path(..., ge=1, description="Target Grade/Role ID"),
    current_user: dict = Depends(get_current_user),
):
    require_hr(current_user)
    grade_repo = GradeRepository()
    try:
        target_grade = grade_repo.get_grade(role_id)
        if not target_grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target role/grade with ID {role_id} not found.",
            )

        role_fit_svc = RoleFitService()
        candidates = role_fit_svc.get_candidates_for_role(role_id)

        formatted_candidates = [
            {
                "employee_id": c.employee_id,
                "name": c.name,
                "current_grade": c.current_grade,
                "target_grade": c.target_grade,
                "role_fit_score": c.role_fit_score,
                "readiness_score": c.readiness_score,
                "promotion_probability": c.promotion_probability,
                "eligibility": c.eligibility,
                "status": c.status,
                "breakdown": c.breakdown,
            }
            for c in candidates
        ]

        return {
            "target_role_id": role_id,
            "target_role_name": target_grade["grade_name"],
            "description": target_grade.get("description"),
            "total_candidates": len(formatted_candidates),
            "candidates": formatted_candidates,
        }
    finally:
        grade_repo.close()


@router.get(
    "/employees/{employee_id}/career-analysis",
    status_code=status.HTTP_200_OK,
    summary="Get detailed employee career analysis for HR",
)
def get_employee_career_analysis_for_hr(
    employee_id: int = Path(..., ge=1),
    current_user: dict = Depends(get_current_user),
):
    require_hr(current_user)
    service = CareerService()
    analysis = service.get_career_analysis(employee_id)
    promotion_status = build_hr_promotion_status(analysis)
    analysis["promotion_status_hr"] = promotion_status
    return analysis


@router.get(
    "/employees/{employee_id}/promotion-status",
    status_code=status.HTTP_200_OK,
    summary="Get employee promotion status in THIRD PERSON messaging",
)
def get_employee_promotion_status_for_hr(
    employee_id: int = Path(..., ge=1),
    current_user: dict = Depends(get_current_user),
):
    require_hr(current_user)
    service = CareerService()
    analysis = service.get_career_analysis(employee_id)
    return build_hr_promotion_status(analysis)


@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get HR talent pipeline analytics",
)
def get_hr_analytics(current_user: dict = Depends(get_current_user)):
    require_hr(current_user)
    emp_repo = EmployeeRepository()
    grade_repo = GradeRepository()
    try:
        employees = emp_repo.get_all_employees()
        grades = grade_repo.get_all_grades()

        total = len(employees)
        grade_dist = {}
        for e in employees:
            g = e.get("current_grade", "Unknown")
            grade_dist[g] = grade_dist.get(g, 0) + 1

        return {
            "total_employees": total,
            "available_roles": len(grades),
            "grade_distribution": grade_dist,
            "average_performance": round(
                sum(float(e.get("performance_rating", 0)) for e in employees) / max(1, total), 2
            ),
        }
    finally:
        emp_repo.close()
        grade_repo.close()
