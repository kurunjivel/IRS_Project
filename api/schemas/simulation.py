"""
Pydantic schemas for Employee What-If Career Scenario Simulator (Phase 1.3).
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillOverrideSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_name: str = Field(..., description="Name of the skill to simulate")
    simulated_level: int = Field(..., ge=1, le=5, description="Simulated skill level (1-5)")


class CertificationOverrideSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certification_name: str = Field(..., description="Name of the certification to simulate")
    completed: bool = Field(True, description="Whether certification is simulated as completed")


class ProjectOverrideSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    additional_projects: int = Field(0, ge=0, le=20, description="Additional completed projects")
    additional_lead_projects: int = Field(0, ge=0, le=10, description="Additional leadership projects")


class ExperienceOverrideSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    additional_experience_years: float = Field(0.0, ge=0.0, le=20.0, description="Additional experience years")


class SimulationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: Optional[int] = Field(None, description="Target employee ID (defaults to current user if omitted)")
    skills: list[SkillOverrideSchema] = Field(default_factory=list, description="List of skill level overrides")
    certifications: list[CertificationOverrideSchema] = Field(default_factory=list, description="List of certification overrides")
    projects: Optional[ProjectOverrideSchema] = Field(None, description="Project experience additions")
    experience: Optional[ExperienceOverrideSchema] = Field(None, description="Experience additions")
    target_grade_id: Optional[int] = Field(None, description="Optional target grade ID override")


class SimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int = Field(..., description="Employee primary key ID")
    employee_name: str = Field(..., description="Employee full name")
    current_grade: str = Field(..., description="Current job grade")
    target_grade: str = Field(..., description="Target job grade")

    baseline_readiness_score: float = Field(..., description="Current baseline readiness score (0-100)")
    simulated_readiness_score: float = Field(..., description="Simulated readiness score (0-100)")
    readiness_score_diff: float = Field(..., description="Difference in readiness score (+/-)")

    baseline_promotion_probability: float = Field(..., description="Current ML promotion probability (0.0-1.0)")
    simulated_promotion_probability: float = Field(..., description="Simulated ML promotion probability (0.0-1.0)")
    probability_diff: float = Field(..., description="Difference in promotion probability (+/-)")

    baseline_readiness_level: str = Field(..., description="Current readiness level classification")
    simulated_readiness_level: str = Field(..., description="Simulated readiness level classification")

    baseline_prediction: str = Field(..., description="Current ML prediction label")
    simulated_prediction: str = Field(..., description="Simulated ML prediction label")

    resolved_skill_gaps: list[str] = Field(default_factory=list, description="Skill requirements satisfied or improved")
    resolved_certifications: list[str] = Field(default_factory=list, description="Certifications satisfied in simulation")
    simulated_shap_summary: Optional[str] = Field(None, description="SHAP feature impact summary for simulated state")
