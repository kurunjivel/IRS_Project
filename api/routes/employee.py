"""
Employee API route handler.
"""

import logging
from fastapi import APIRouter, Path, status
from api.schemas.employee import EmployeeResponse
from services.career_service import CareerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Employee"])


@router.get(
    "/employee/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get employee profile",
    description="Retrieve employee details including skills, certifications, and project experience.",
)
def get_employee(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
) -> EmployeeResponse:
    """Fetch employee profile by employee ID."""
    logger.info("API GET /employee/%s requested", employee_id)
    service = CareerService()
    employee = service.get_employee(employee_id)
    return EmployeeResponse.model_validate(employee)
