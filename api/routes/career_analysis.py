"""
Career Analysis Combined Endpoint API route handler.
"""

import logging
from fastapi import APIRouter, Path, status
from api.schemas.career_analysis import CareerAnalysisResponse
from services.career_service import CareerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Career Analysis"])


@router.get(
    "/career-analysis/{employee_id}",
    response_model=CareerAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comprehensive career analysis",
    description="Combined endpoint returning employee profile, gap analysis, readiness score, ML prediction, and hybrid recommendations.",
)
def get_career_analysis(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
) -> CareerAnalysisResponse:
    """Run full end-to-end career analysis for employee."""
    logger.info("API GET /career-analysis/%s requested", employee_id)
    service = CareerService()
    result = service.get_career_analysis(employee_id)
    return CareerAnalysisResponse.model_validate(result)
