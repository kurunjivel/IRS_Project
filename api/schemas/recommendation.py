"""
Recommendation Pydantic schemas.
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    type: str = Field(..., description="Category (Learning, Certification, Project, Mentorship)")
    title: str = Field(..., description="Title of the recommended item")
    reason: str = Field(..., description="Explanation for recommendation and priority")
    priority: str = Field(..., description="Assigned priority level (HIGH, MEDIUM, LOW)")
    provider: Optional[str] = Field("", description="Source or provider")
    duration: Optional[str] = Field("", description="Expected time duration")
    impact: Optional[str] = Field("", description="Calculated impact description")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="Additional item metadata")


class TimelineMilestoneSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    month: int = Field(..., description="Milestone month number")
    title: str = Field(..., description="Milestone title")
    description: str = Field(..., description="Milestone description")
    category: str = Field(..., description="Milestone category")


class RecommendationSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(..., ge=0, description="Total count of recommendations")
    high: int = Field(..., ge=0, description="Count of HIGH priority recommendations")
    medium: int = Field(..., ge=0, description="Count of MEDIUM priority recommendations")
    low: int = Field(..., ge=0, description="Count of LOW priority recommendations")


class RecommendationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    urgency: str = Field(..., description="Urgency label (Immediate, High, Moderate, Maintenance)")
    learning: list[RecommendationItemSchema] = Field(default_factory=list, description="Learning path and course recommendations")
    certifications: list[RecommendationItemSchema] = Field(default_factory=list, description="Certification recommendations")
    projects: list[RecommendationItemSchema] = Field(default_factory=list, description="Project recommendations")
    mentors: list[RecommendationItemSchema] = Field(default_factory=list, description="Mentorship recommendations")
    summary: RecommendationSummarySchema = Field(..., description="Priority breakdown summary")
    timeline: list[TimelineMilestoneSchema] = Field(default_factory=list, description="Career milestone timeline")
