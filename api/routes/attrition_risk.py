"""
Phase 9 — Employee Attrition & Flight-Risk Prediction API Routes.
"""

import logging
from fastapi import APIRouter, Depends, Path, status, HTTPException

from api.dependencies import get_current_user, require_employee, require_hr
from services.career_service import CareerService
from services.gap_analysis_service import EmployeeNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Attrition & Career Stability"])


@router.get(
    "/employee/me/attrition-risk",
    status_code=status.HTTP_200_OK,
    summary="Get my career stability & flight-risk indicators",
    description="Retrieve personal career stability indicators, positive/negative growth factors, and data readiness report using non-alarming language.",
)
def get_my_attrition_risk(current_user: dict = Depends(get_current_user)):
    """Retrieve authenticated employee's career stability indicators."""
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    logger.info("API GET /employee/me/attrition-risk requested by emp_id=%s", emp_id)
    service = CareerService()
    try:
        return service.get_attrition_risk(emp_id)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("Error evaluating career stability for %s: %s", emp_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/hr/employees/{employee_id}/attrition-risk",
    status_code=status.HTTP_200_OK,
    summary="Get employee flight-risk analysis for HR",
    description="Retrieve flight-risk prediction and contributing factors for a specific employee.",
)
def get_employee_attrition_risk_hr(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve specific employee flight risk for HR."""
    require_hr(current_user)
    logger.info("API GET /hr/employees/%s/attrition-risk requested by HR", employee_id)
    service = CareerService()
    try:
        return service.get_attrition_risk(employee_id)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("Error evaluating flight risk for %s: %s", employee_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/hr/analytics/attrition-distribution",
    status_code=status.HTTP_200_OK,
    summary="Get organizational flight-risk distribution for HR Dashboard",
    description="Retrieve aggregated Low, Moderate, and High flight-risk counts across the organization.",
)
def get_organizational_attrition_distribution(current_user: dict = Depends(get_current_user)):
    """Retrieve organizational flight-risk distribution for HR."""
    require_hr(current_user)
    logger.info("API GET /hr/analytics/attrition-distribution requested by HR")
    service = CareerService()
    try:
        return service.get_organizational_attrition_risk()
    except Exception as e:
        logger.error("Error generating organizational flight risk distribution: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
