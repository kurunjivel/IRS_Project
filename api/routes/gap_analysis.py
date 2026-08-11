"""
Gap Analysis API route handler.
"""

import logging
from fastapi import APIRouter, Path, status
from api.schemas.gap_analysis import GapAnalysisResponse
from services.career_service import CareerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Gap Analysis"])


@router.get(
    "/gap-analysis/{employee_id}",
    response_model=GapAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get gap analysis",
    description="Retrieve Phase 2 gap analysis detailing skill, certification, experience, and project deficits.",
)
def get_gap_analysis(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
) -> GapAnalysisResponse:
    """Run gap analysis for the employee."""
    logger.info("API GET /gap-analysis/%s requested", employee_id)
    service = CareerService()
    result = service.get_gap_analysis(employee_id)
    return GapAnalysisResponse.model_validate(result)
