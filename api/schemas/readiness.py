"""
Readiness Scoring Pydantic schemas.
"""

from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.employee import EmployeeSummarySchema


class SkillScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(..., description="Calculated skill readiness score (0-40)")
    max_score: float = Field(..., description="Maximum possible skill score (40)")
    percentage: float = Field(..., description="Skill coverage percentage")
    missing_skills: list[str] = Field(default_factory=list, description="Names of missing required skills")
    weight: float = Field(..., description="Category weight in final readiness score")


class CertificationScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(..., description="Calculated certification readiness score (0-15)")
    max_score: float = Field(..., description="Maximum possible certification score (15)")
    completed: int = Field(..., description="Completed certifications count")
    missing: list[str] = Field(default_factory=list, description="Missing certification names")
    weight: float = Field(..., description="Category weight in final readiness score")


class ExperienceScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(..., description="Calculated experience readiness score (0-15)")
    current_years: float = Field(..., description="Current experience years")
    required_years: float = Field(..., description="Required experience years")
    gap_years: float = Field(..., description="Gap in experience years")
    weight: float = Field(..., description="Category weight in final readiness score")


class ProjectScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(..., description="Calculated project readiness score (0-20)")
    completed: int = Field(..., description="Completed projects count")
    required: int = Field(..., description="Required projects count")
    remaining: int = Field(..., description="Remaining projects needed")
    lead_completed: int = Field(..., description="Lead projects completed count")
    lead_required: int = Field(..., description="Lead projects required count")
    lead_remaining: int = Field(..., description="Lead projects remaining needed")
    weight: float = Field(..., description="Category weight in final readiness score")


class PerformanceScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(..., description="Calculated performance score (0-10)")
    performance_rating: float = Field(..., description="Employee latest performance rating")
    weight: float = Field(..., description="Category weight in final readiness score")


class ReadinessBreakdownSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skills: SkillScoreSchema = Field(..., description="Skill score breakdown")
    certifications: CertificationScoreSchema = Field(..., description="Certification score breakdown")
    experience: ExperienceScoreSchema = Field(..., description="Experience score breakdown")
    projects: ProjectScoreSchema = Field(..., description="Project score breakdown")
    performance: PerformanceScoreSchema = Field(..., description="Performance score breakdown")


class ReadinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee: dict[str, Any] = Field(..., description="Employee summary information")
    readiness_score: float = Field(..., ge=0.0, le=100.0, description="Overall promotion readiness score (0-100)")
    readiness_level: str = Field(..., description="Readiness level classification (e.g., Promotion Ready, Almost Ready)")
    promotion_decision: str = Field(..., description="Promotion decision classification (Ready, Conditional, Not Ready)")
    breakdown: ReadinessBreakdownSchema = Field(..., description="Detailed category breakdown of readiness score")
