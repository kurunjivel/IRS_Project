"""
GradeRequirement model.

Represents all requirements that must be met to achieve a target grade.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GradeSkillRequirement:
    """A single skill requirement for a grade."""

    skill_name: str
    category: str
    required_level: int
    weight: float
    mandatory: bool


@dataclass
class GradeCertificationRequirement:
    """A single certification requirement for a grade."""

    certification_name: str
    provider: str
    mandatory: bool


@dataclass
class GradeProjectRequirement:
    """Project and experience thresholds required for a grade."""

    minimum_projects: int
    minimum_lead_projects: int
    minimum_experience: float


@dataclass
class GradeRequirement:
    """
    Full set of requirements for a target grade.

    Attributes:
        grade_id:             Primary key of the grade.
        grade_name:           Human-readable grade name.
        description:          Grade description.
        skills:               List of required skills with levels.
        certifications:       List of required certifications.
        project_requirement:  Project and experience thresholds.
    """

    grade_id: int
    grade_name: str
    description: Optional[str]
    skills: list[GradeSkillRequirement] = field(default_factory=list)
    certifications: list[GradeCertificationRequirement] = field(default_factory=list)
    project_requirement: Optional[GradeProjectRequirement] = None
