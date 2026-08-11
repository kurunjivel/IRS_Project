"""
Gap Analysis Pydantic schemas.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.employee import EmployeeSummarySchema


class SkillGapSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill: str = Field(..., description="Skill name")
    category: str = Field(..., description="Skill category")
    current_level: int = Field(..., description="Current skill level of employee")
    required_level: int = Field(..., description="Required skill level for target grade")
    gap: int = Field(..., description="Deficit level (required - current)")
    mandatory: bool = Field(..., description="Whether skill is mandatory for target grade")


class CertificationGapSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certification: str = Field(..., description="Certification name required")
    provider: str = Field(..., description="Certification provider")
    mandatory: bool = Field(..., description="Whether certification is mandatory for target grade")


class ExperienceGapSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_years: float = Field(..., description="Current experience years")
    required_years: float = Field(..., description="Required experience years for target grade")
    remaining_years: float = Field(..., description="Remaining experience years required")


class ProjectGapSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_projects: int = Field(..., description="Total completed projects by employee")
    lead_projects: int = Field(..., description="Lead projects completed by employee")
    required_projects: int = Field(..., description="Required projects for target grade")
    required_lead_projects: int = Field(..., description="Required lead projects for target grade")
    remaining_projects: int = Field(..., description="Remaining total projects needed")
    remaining_lead_projects: int = Field(..., description="Remaining lead projects needed")


class GapAnalysisDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skills: list[SkillGapSchema] = Field(default_factory=list, description="Skill gap items")
    certifications: list[CertificationGapSchema] = Field(default_factory=list, description="Certification gap items")
    experience: ExperienceGapSchema = Field(..., description="Experience gap analysis")
    projects: ProjectGapSchema = Field(..., description="Project gap analysis")


class GapAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee: EmployeeSummarySchema = Field(..., description="Employee summary")
    gapAnalysis: GapAnalysisDetailSchema = Field(..., description="Gap analysis details")
