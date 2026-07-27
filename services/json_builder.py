"""
JSON builder service.

Converts the raw gap analysis dictionary produced by GapAnalysisService
into a clean, serialisable JSON-ready dictionary.
"""

import logging

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class JsonBuilder:
    """Converts gap analysis results into a structured JSON-ready dict."""

    def build(self, analysis: dict) -> dict:
        """
        Build the final JSON-ready gap analysis report.

        Args:
            analysis: The dict returned by GapAnalysisService.run().

        Returns:
            A fully serialisable dict matching the expected report structure.
        """
        employee: Employee = analysis["employee"]
        requirement: GradeRequirement = analysis["requirement"]

        report = {
            "employee": {
                "employee_id": employee.employee_id,
                "employee_code": employee.employee_code,
                "full_name": employee.full_name,
                "email": employee.email,
                "department": employee.department,
                "experience_years": employee.experience_years,
                "performance_rating": employee.performance_rating,
                "joining_date": employee.joining_date,
                "current_grade": employee.current_grade,
                "target_grade": employee.target_grade,
            },
            "gapAnalysis": {
                "skills": self._build_skill_gaps(analysis["skill_gaps"]),
                "certifications": self._build_cert_gaps(analysis["certification_gaps"]),
                "experience": self._build_experience_gap(analysis["experience_gap"]),
                "projects": self._build_project_gap(analysis["project_gap"]),
            },
        }

        logger.info("JSON report built for employee %s.", employee.employee_id)
        return report

    def _build_skill_gaps(self, skill_gaps: list[dict]) -> list[dict]:
        """
        Format skill gaps for the report.

        Args:
            skill_gaps: Raw list from SkillGapService.

        Returns:
            List of formatted skill gap dicts.
        """
        return [
            {
                "skill": g["skill"],
                "category": g["category"],
                "current_level": g["current_level"],
                "required_level": g["required_level"],
                "gap": g["gap"],
                "mandatory": g["mandatory"],
            }
            for g in skill_gaps
        ]

    def _build_cert_gaps(self, cert_gaps: list[dict]) -> list[dict]:
        """
        Format certification gaps for the report.

        Args:
            cert_gaps: Raw list from CertificationGapService.

        Returns:
            List of formatted certification gap dicts.
        """
        return [
            {
                "certification": g["certification"],
                "provider": g["provider"],
                "mandatory": g["mandatory"],
            }
            for g in cert_gaps
        ]

    def _build_experience_gap(self, exp_gap: dict) -> dict:
        """
        Format experience gap for the report.

        Args:
            exp_gap: Raw dict from ExperienceGapService.

        Returns:
            Formatted experience gap dict.
        """
        return {
            "current_years": exp_gap["current_years"],
            "required_years": exp_gap["required_years"],
            "remaining_years": exp_gap["remaining_years"],
        }

    def _build_project_gap(self, proj_gap: dict) -> dict:
        """
        Format project gap for the report.

        Args:
            proj_gap: Raw dict from ProjectGapService.

        Returns:
            Formatted project gap dict.
        """
        return {
            "total_projects": proj_gap["total_projects"],
            "lead_projects": proj_gap["lead_projects"],
            "required_projects": proj_gap["required_projects"],
            "required_lead_projects": proj_gap["required_lead_projects"],
            "remaining_projects": proj_gap["remaining_projects"],
            "remaining_lead_projects": proj_gap["remaining_lead_projects"],
        }
