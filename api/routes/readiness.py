"""
Readiness Scoring API route handler.
"""

import logging
from fastapi import APIRouter, Path, status
from api.schemas.readiness import ReadinessResponse
from services.career_service import CareerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Readiness"])


@router.get(
    "/readiness/{employee_id}",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get promotion readiness score",
    description="Retrieve Phase 3 readiness score (0-100), level, promotion decision, and category breakdowns.",
)
def get_readiness(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
) -> ReadinessResponse:
    """Calculate promotion readiness score for employee."""
    logger.info("API GET /readiness/%s requested", employee_id)
    service = CareerService()
    result = service.get_readiness(employee_id)
    return ReadinessResponse.model_validate(result)
