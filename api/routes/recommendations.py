"""
Hybrid Recommendations API route handler.
"""

import logging
from fastapi import APIRouter, Path, status
from api.schemas.recommendation import RecommendationsResponse
from services.career_service import CareerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Recommendations"])


@router.get(
    "/recommendations/{employee_id}",
    response_model=RecommendationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get hybrid career recommendations",
    description="Retrieve Phase 6 hybrid recommendations for courses, certifications, projects, mentors, and milestone timeline.",
)
def get_recommendations(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
) -> RecommendationsResponse:
    """Generate hybrid recommendation plan for employee."""
    logger.info("API GET /recommendations/%s requested", employee_id)
    service = CareerService()
    result = service.get_recommendations(employee_id)
    return RecommendationsResponse.model_validate(result)
