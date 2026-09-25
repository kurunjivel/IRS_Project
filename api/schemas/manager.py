"""
Pydantic Schemas for Manager Portal endpoints — Phase 1 Enhancement 4.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


class ManagerReviewSubmitRequest(BaseModel):
    employee_id: int = Field(..., description="Target employee ID")
    quarter: str = Field("Q3-2026", description="Evaluation quarter, e.g. Q3-2026")
    status: str = Field(..., description="Review decision: PENDING, IN_REVIEW, APPROVED, REJECTED, NEEDS_DEVELOPMENT")
    technical_competency: int = Field(3, ge=1, le=5, description="Technical competency rating (1-5)")
    communication: int = Field(3, ge=1, le=5, description="Communication rating (1-5)")
    leadership: int = Field(3, ge=1, le=5, description="Leadership rating (1-5)")
    teamwork: int = Field(3, ge=1, le=5, description="Teamwork rating (1-5)")
    ownership: int = Field(3, ge=1, le=5, description="Ownership rating (1-5)")
    overall_assessment: Optional[str] = Field(None, description="General narrative feedback")
    comments: Optional[str] = Field(None, description="Specific feedback (mandatory on REJECTED or NEEDS_DEVELOPMENT)")


class ManagerTeamMemberResponse(BaseModel):
    employee_id: int
    full_name: str
    email: str
    department: str
    current_grade: str
    target_grade: str
    readiness_score: float
    promotion_probability: float
    review_status: str
    review_details: Optional[dict] = None


class ManagerReviewSubmitResponse(BaseModel):
    message: str
    review: dict
    audit: dict
