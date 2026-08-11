"""
API Route routers for Phase 7 FastAPI API layer.
"""

from api.routes.employee import router as employee_router
from api.routes.gap_analysis import router as gap_analysis_router
from api.routes.readiness import router as readiness_router
from api.routes.prediction import router as prediction_router
from api.routes.recommendations import router as recommendations_router
from api.routes.career_analysis import router as career_analysis_router

__all__ = [
    "employee_router",
    "gap_analysis_router",
    "readiness_router",
    "prediction_router",
    "recommendations_router",
    "career_analysis_router",
]
