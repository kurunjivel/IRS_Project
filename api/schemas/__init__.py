"""
Pydantic response models and schemas for Phase 7 FastAPI API layer.
"""

from api.schemas.employee import (
    EmployeeSkillSchema,
    EmployeeCertificationSchema,
    EmployeeProjectSchema,
    EmployeeResponse,
    EmployeeSummarySchema,
)
from api.schemas.gap_analysis import (
    SkillGapSchema,
    CertificationGapSchema,
    ExperienceGapSchema,
    ProjectGapSchema,
    GapAnalysisDetailSchema,
    GapAnalysisResponse,
)
from api.schemas.readiness import ReadinessResponse
from api.schemas.prediction import PredictionResponse
from api.schemas.recommendation import (
    RecommendationItemSchema,
    TimelineMilestoneSchema,
    RecommendationSummarySchema,
    RecommendationsResponse,
)
from api.schemas.career_analysis import CareerAnalysisResponse

__all__ = [
    "EmployeeSkillSchema",
    "EmployeeCertificationSchema",
    "EmployeeProjectSchema",
    "EmployeeResponse",
    "EmployeeSummarySchema",
    "SkillGapSchema",
    "CertificationGapSchema",
    "ExperienceGapSchema",
    "ProjectGapSchema",
    "GapAnalysisDetailSchema",
    "GapAnalysisResponse",
    "ReadinessResponse",
    "PredictionResponse",
    "RecommendationItemSchema",
    "TimelineMilestoneSchema",
    "RecommendationSummarySchema",
    "RecommendationsResponse",
    "CareerAnalysisResponse",
]
