"""
Employee Pydantic schemas.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmployeeSkillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_name: str = Field(..., description="Name of the skill")
    category: str = Field(..., description="Skill category")
    skill_level: int = Field(..., ge=1, le=5, description="Proficiency level (1-5)")


class EmployeeCertificationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certification_name: str = Field(..., description="Name of the certification")
    provider: str = Field(..., description="Certification provider/issuing organization")
    status: str = Field(..., description="Status (e.g. Completed, In Progress)")
    completion_date: Optional[str] = Field(None, description="Completion date string")
    expiry_date: Optional[str] = Field(None, description="Expiry date string")


class EmployeeProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_name: str = Field(..., description="Name of the project")
    technology: str = Field(..., description="Primary technology used")
    difficulty: str = Field(..., description="Project difficulty")
    domain: str = Field(..., description="Project domain")
    role: str = Field(..., description="Role played in project")
    lead_project: bool = Field(..., description="Whether employee led the project")
    duration_months: int = Field(..., ge=0, description="Duration in months")
    project_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Project performance rating")


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int = Field(..., description="Employee primary key ID")
    employee_code: str = Field(..., description="Unique employee code")
    full_name: str = Field(..., description="Employee full name")
    email: str = Field(..., description="Employee corporate email")
    department: str = Field(..., description="Department name")
    experience_years: float = Field(..., ge=0.0, description="Total years of professional experience")
    performance_rating: float = Field(..., ge=1.0, le=5.0, description="Latest performance rating")
    joining_date: str = Field(..., description="Joining date string")
    current_grade: str = Field(..., description="Current job grade")
    current_grade_id: int = Field(..., description="Current grade ID")
    target_grade: str = Field(..., description="Target promotion grade")
    target_grade_id: int = Field(..., description="Target grade ID")
    skills: list[EmployeeSkillSchema] = Field(default_factory=list, description="List of held skills")
    certifications: list[EmployeeCertificationSchema] = Field(default_factory=list, description="List of held certifications")
    projects: list[EmployeeProjectSchema] = Field(default_factory=list, description="List of completed projects")


class EmployeeSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int = Field(..., description="Employee primary key ID")
    employee_code: str = Field(..., description="Unique employee code")
    full_name: str = Field(..., description="Employee full name")
    email: Optional[str] = Field(None, description="Employee corporate email")
    department: str = Field(..., description="Department name")
    current_grade: str = Field(..., description="Current job grade")
    target_grade: str = Field(..., description="Target promotion grade")
    experience_years: float = Field(..., description="Total years of professional experience")
    performance_rating: float = Field(..., description="Latest performance rating")
    joining_date: Optional[str] = Field(None, description="Joining date string")
