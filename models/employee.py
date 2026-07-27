"""
Employee model.

Represents a fully loaded employee including their skills,
certifications, and projects.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EmployeeSkill:
    """A single skill held by an employee."""

    skill_name: str
    category: str
    skill_level: int


@dataclass
class EmployeeCertification:
    """A single certification held by an employee."""

    certification_name: str
    provider: str
    status: str
    completion_date: Optional[str]
    expiry_date: Optional[str]


@dataclass
class EmployeeProject:
    """A single project an employee has participated in."""

    project_name: str
    technology: str
    difficulty: str
    domain: str
    role: str
    lead_project: bool
    duration_months: int
    project_rating: Optional[float]


@dataclass
class Employee:
    """
    Full employee profile loaded from the database.

    Attributes:
        employee_id:        Primary key.
        employee_code:      Unique employee code.
        full_name:          Full name.
        email:              Email address.
        department:         Department name.
        experience_years:   Total years of professional experience.
        performance_rating: Latest performance rating.
        joining_date:       Date the employee joined the company.
        current_grade:      Name of the employee's current grade.
        current_grade_id:   ID of the current grade.
        target_grade:       Name of the employee's target grade.
        target_grade_id:    ID of the target grade.
        skills:             List of skills the employee holds.
        certifications:     List of certifications the employee holds.
        projects:           List of projects the employee has worked on.
    """

    employee_id: int
    employee_code: str
    full_name: str
    email: str
    department: str
    experience_years: float
    performance_rating: float
    joining_date: str
    current_grade: str
    current_grade_id: int
    target_grade: str
    target_grade_id: int
    skills: list[EmployeeSkill] = field(default_factory=list)
    certifications: list[EmployeeCertification] = field(default_factory=list)
    projects: list[EmployeeProject] = field(default_factory=list)
