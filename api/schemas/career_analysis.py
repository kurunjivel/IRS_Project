"""
Career Analysis Combined Endpoint Pydantic schemas.
"""

from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.prediction import PredictionResponse
from api.schemas.recommendation import RecommendationsResponse


class CareerAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee: dict[str, Any] = Field(..., description="Employee profile details")
    gap_analysis: dict[str, Any] = Field(..., description="Gap analysis report details")
    readiness: dict[str, Any] = Field(..., description="Readiness scoring and breakdown")
    prediction: PredictionResponse = Field(..., description="ML promotion prediction result")
    recommendations: RecommendationsResponse = Field(..., description="Hybrid recommendation plan and timeline")
