"""
ML Promotion Prediction API route handler.
"""

import logging
from fastapi import APIRouter, Path, status
from api.schemas.prediction import PredictionResponse
from services.career_service import CareerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Prediction"])


@router.get(
    "/prediction/{employee_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get promotion ML prediction",
    description="Retrieve Phase 5 machine learning promotion prediction and progression probability.",
)
def get_prediction(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
) -> PredictionResponse:
    """Predict promotion probability for employee using ML model."""
    logger.info("API GET /prediction/%s requested", employee_id)
    service = CareerService()
    result = service.get_prediction(employee_id)
    return PredictionResponse.model_validate(result)
