"""
Unit tests for the IRS Phase 2 Gap Analysis Engine.

All tests use mocked repositories — no live database required.
mysql.connector is stubbed out before any service import so the
test suite runs without a MySQL installation.
"""

import sys
import unittest
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Stub mysql.connector before any project module is imported
# ---------------------------------------------------------------------------
_mysql_stub = MagicMock()
sys.modules.setdefault("mysql", _mysql_stub)
sys.modules.setdefault("mysql.connector", _mysql_stub)
sys.modules.setdefault("mysql.connector.pooling", _mysql_stub)

from models.employee import Employee, EmployeeSkill, EmployeeCertification, EmployeeProject
from models.grade_requirement import (
    GradeRequirement,
    GradeSkillRequirement,
    GradeCertificationRequirement,
    GradeProjectRequirement,
)
from services.skill_gap_service import SkillGapService
from services.certification_gap_service import CertificationGapService
from services.experience_gap_service import ExperienceGapService
from services.project_gap_service import ProjectGapService
from services.gap_analysis_service import GapAnalysisService, EmployeeNotFoundError, GradeNotFoundError
from services.json_builder import JsonBuilder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_employee(**overrides) -> Employee:
    """Return a base Employee with sensible defaults."""
    defaults = dict(
        employee_id=1,
        employee_code="EMP001",
        full_name="Alice Smith",
        email="alice@example.com",
        department="Engineering",
        experience_years=3.0,
        performance_rating=4.0,
        joining_date="2021-01-01",
        current_grade="Grade B",
        current_grade_id=2,
        target_grade="Grade A",
        target_grade_id=1,
        skills=[],
        certifications=[],
        projects=[],
    )
    defaults.update(overrides)
    return Employee(**defaults)


def make_requirement(**overrides) -> GradeRequirement:
    """Return a base GradeRequirement with sensible defaults."""
    defaults = dict(
        grade_id=1,
        grade_name="Grade A",
        description="Senior level",
        skills=[],
        certifications=[],
        project_requirement=GradeProjectRequirement(
            minimum_projects=3,
            minimum_lead_projects=1,
            minimum_experience=5.0,
        ),
    )
    defaults.update(overrides)
    return GradeRequirement(**defaults)


# ---------------------------------------------------------------------------
# SkillGapService
# ---------------------------------------------------------------------------

class TestSkillGapService(unittest.TestCase):
    """Tests for SkillGapService."""

    def setUp(self) -> None:
        self.service = SkillGapService()

    def test_no_required_skills_returns_empty(self) -> None:
        """No gaps when the grade has no skill requirements."""
        gaps = self.service.analyze(make_employee(), make_requirement())
        self.assertEqual(gaps, [])

    def test_employee_has_all_skills(self) -> None:
        """No gaps when employee meets or exceeds all required skill levels."""
        employee = make_employee(skills=[
            EmployeeSkill("Python", "Backend", 5),
            EmployeeSkill("Java", "Backend", 4),
        ])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Python", "Backend", 5, 1.0, True),
            GradeSkillRequirement("Java", "Backend", 3, 0.8, False),
        ])
        self.assertEqual(self.service.analyze(employee, requirement), [])

    def test_employee_exceeds_skill_level(self) -> None:
        """No gap when employee level is higher than required."""
        employee = make_employee(skills=[EmployeeSkill("Python", "Backend", 5)])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Python", "Backend", 3, 1.0, True),
        ])
        self.assertEqual(self.service.analyze(employee, requirement), [])

    def test_employee_missing_skill_entirely(self) -> None:
        """Gap reported with current_level=0 for a skill the employee lacks."""
        employee = make_employee(skills=[EmployeeSkill("Python", "Backend", 3)])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Python", "Backend", 3, 1.0, True),
            GradeSkillRequirement("Java", "Backend", 5, 1.0, True),
        ])
        gaps = self.service.analyze(employee, requirement)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["skill"], "Java")
        self.assertEqual(gaps[0]["current_level"], 0)
        self.assertEqual(gaps[0]["gap"], 5)

    def test_employee_skill_level_insufficient(self) -> None:
        """Gap reported when employee has the skill but below required level."""
        employee = make_employee(skills=[EmployeeSkill("Java", "Backend", 3)])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Java", "Backend", 5, 1.0, True),
        ])
        gaps = self.service.analyze(employee, requirement)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["current_level"], 3)
        self.assertEqual(gaps[0]["required_level"], 5)
        self.assertEqual(gaps[0]["gap"], 2)

    def test_multiple_skill_gaps(self) -> None:
        """All insufficient skills are reported."""
        employee = make_employee(skills=[
            EmployeeSkill("Java", "Backend", 2),
            EmployeeSkill("AWS", "Cloud", 1),
        ])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Java", "Backend", 5, 1.0, True),
            GradeSkillRequirement("AWS", "Cloud", 4, 0.8, False),
        ])
        gaps = self.service.analyze(employee, requirement)
        self.assertEqual(len(gaps), 2)

    def test_skill_name_comparison_is_case_insensitive(self) -> None:
        """Skill matching ignores case differences."""
        employee = make_employee(skills=[EmployeeSkill("python", "Backend", 5)])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Python", "Backend", 5, 1.0, True),
        ])
        self.assertEqual(self.service.analyze(employee, requirement), [])

    def test_gap_dict_contains_mandatory_flag(self) -> None:
        """Each gap dict includes the mandatory flag from the requirement."""
        employee = make_employee(skills=[])
        requirement = make_requirement(skills=[
            GradeSkillRequirement("Docker", "DevOps", 3, 0.5, False),
        ])
        gaps = self.service.analyze(employee, requirement)
        self.assertFalse(gaps[0]["mandatory"])


# ---------------------------------------------------------------------------
# CertificationGapService
# ---------------------------------------------------------------------------

class TestCertificationGapService(unittest.TestCase):
    """Tests for CertificationGapService."""

    def setUp(self) -> None:
        self.service = CertificationGapService()

    def test_no_required_certifications_returns_empty(self) -> None:
        """No gaps when the grade has no certification requirements."""
        self.assertEqual(self.service.analyze(make_employee(), make_requirement()), [])

    def test_employee_has_all_certifications(self) -> None:
        """No gaps when employee holds all required certifications."""
        employee = make_employee(certifications=[
            EmployeeCertification("AWS-CCP", "Amazon", "Completed", "2023-01-01", None),
        ])
        requirement = make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
        ])
        self.assertEqual(self.service.analyze(employee, requirement), [])

    def test_employee_missing_certification(self) -> None:
        """Gap reported for a certification the employee does not hold."""
        employee = make_employee(certifications=[])
        requirement = make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
        ])
        gaps = self.service.analyze(employee, requirement)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["certification"], "AWS-CCP")
        self.assertEqual(gaps[0]["provider"], "Amazon")
        self.assertTrue(gaps[0]["mandatory"])

    def test_incomplete_certification_counts_as_missing(self) -> None:
        """A certification with status != 'Completed' is treated as missing."""
        employee = make_employee(certifications=[
            EmployeeCertification("AWS-CCP", "Amazon", "In Progress", None, None),
        ])
        requirement = make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
        ])
        self.assertEqual(len(self.service.analyze(employee, requirement)), 1)

    def test_certification_status_case_insensitive(self) -> None:
        """'completed' (lowercase) is accepted as a valid completion status."""
        employee = make_employee(certifications=[
            EmployeeCertification("AWS-CCP", "Amazon", "completed", "2023-01-01", None),
        ])
        requirement = make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
        ])
        self.assertEqual(self.service.analyze(employee, requirement), [])

    def test_multiple_missing_certifications(self) -> None:
        """All missing certifications are reported."""
        employee = make_employee(certifications=[])
        requirement = make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
            GradeCertificationRequirement("PMP", "PMI", False),
        ])
        self.assertEqual(len(self.service.analyze(employee, requirement)), 2)

    def test_partial_certifications_only_missing_reported(self) -> None:
        """Only the missing certification is reported when one is held."""
        employee = make_employee(certifications=[
            EmployeeCertification("AWS-CCP", "Amazon", "Completed", "2023-01-01", None),
        ])
        requirement = make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
            GradeCertificationRequirement("PMP", "PMI", False),
        ])
        gaps = self.service.analyze(employee, requirement)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["certification"], "PMP")


# ---------------------------------------------------------------------------
# ExperienceGapService
# ---------------------------------------------------------------------------

class TestExperienceGapService(unittest.TestCase):
    """Tests for ExperienceGapService."""

    def setUp(self) -> None:
        self.service = ExperienceGapService()

    def test_employee_meets_experience_exactly(self) -> None:
        """Remaining years is 0 when employee exactly meets the requirement."""
        result = self.service.analyze(make_employee(experience_years=5.0), make_requirement())
        self.assertEqual(result["remaining_years"], 0.0)

    def test_employee_exceeds_experience(self) -> None:
        """Remaining years is 0 when employee exceeds the requirement."""
        result = self.service.analyze(make_employee(experience_years=8.0), make_requirement())
        self.assertEqual(result["remaining_years"], 0.0)

    def test_employee_missing_experience(self) -> None:
        """Remaining years is correctly calculated when experience is short."""
        result = self.service.analyze(make_employee(experience_years=2.0), make_requirement())
        self.assertEqual(result["current_years"], 2.0)
        self.assertEqual(result["required_years"], 5.0)
        self.assertEqual(result["remaining_years"], 3.0)

    def test_remaining_never_negative(self) -> None:
        """Remaining years is never negative."""
        result = self.service.analyze(make_employee(experience_years=10.0), make_requirement())
        self.assertGreaterEqual(result["remaining_years"], 0.0)

    def test_no_project_requirement_defaults_to_zero(self) -> None:
        """Required years defaults to 0 when project_requirement is None."""
        req = make_requirement(project_requirement=None)
        result = self.service.analyze(make_employee(experience_years=0.0), req)
        self.assertEqual(result["required_years"], 0.0)
        self.assertEqual(result["remaining_years"], 0.0)

    def test_result_contains_all_keys(self) -> None:
        """Result dict always contains current_years, required_years, remaining_years."""
        result = self.service.analyze(make_employee(), make_requirement())
        for key in ("current_years", "required_years", "remaining_years"):
            self.assertIn(key, result)


# ---------------------------------------------------------------------------
# ProjectGapService
# ---------------------------------------------------------------------------

class TestProjectGapService(unittest.TestCase):
    """Tests for ProjectGapService."""

    def setUp(self) -> None:
        self.service = ProjectGapService()

    def _make_project(self, name: str, lead: bool = False) -> EmployeeProject:
        return EmployeeProject(name, "Python", "Medium", "Finance", "Dev", lead, 6, 4.0)

    def test_employee_meets_project_requirements(self) -> None:
        """No remaining projects when employee meets all thresholds."""
        projects = [
            EmployeeProject("P1", "Python", "Medium", "Finance", "Dev", False, 6, 4.0),
            EmployeeProject("P2", "Java", "Hard", "Banking", "Lead", True, 12, 5.0),
            EmployeeProject("P3", "AWS", "Easy", "Cloud", "Dev", False, 3, 3.5),
        ]
        result = self.service.analyze(make_employee(projects=projects), make_requirement())
        self.assertEqual(result["remaining_projects"], 0)
        self.assertEqual(result["remaining_lead_projects"], 0)

    def test_employee_missing_projects(self) -> None:
        """Remaining projects correctly calculated when below threshold."""
        employee = make_employee(projects=[self._make_project("P1")])
        result = self.service.analyze(employee, make_requirement())
        self.assertEqual(result["total_projects"], 1)
        self.assertEqual(result["remaining_projects"], 2)
        self.assertEqual(result["remaining_lead_projects"], 1)

    def test_employee_missing_lead_projects_only(self) -> None:
        """Remaining lead projects reported when total is met but leads are not."""
        projects = [self._make_project(f"P{i}") for i in range(3)]  # 3 non-lead
        result = self.service.analyze(make_employee(projects=projects), make_requirement())
        self.assertEqual(result["remaining_projects"], 0)
        self.assertEqual(result["remaining_lead_projects"], 1)

    def test_employee_no_projects(self) -> None:
        """All required projects and lead projects are reported as remaining."""
        result = self.service.analyze(make_employee(projects=[]), make_requirement())
        self.assertEqual(result["remaining_projects"], 3)
        self.assertEqual(result["remaining_lead_projects"], 1)

    def test_remaining_never_negative(self) -> None:
        """Remaining counts are never negative when employee far exceeds requirements."""
        projects = [
            EmployeeProject(f"P{i}", "Python", "Hard", "Cloud", "Lead", True, 6, 5.0)
            for i in range(10)
        ]
        result = self.service.analyze(make_employee(projects=projects), make_requirement())
        self.assertGreaterEqual(result["remaining_projects"], 0)
        self.assertGreaterEqual(result["remaining_lead_projects"], 0)

    def test_no_project_requirement_returns_zeros(self) -> None:
        """All counts are 0 when project_requirement is None."""
        req = make_requirement(project_requirement=None)
        result = self.service.analyze(make_employee(projects=[]), req)
        self.assertEqual(result["remaining_projects"], 0)
        self.assertEqual(result["remaining_lead_projects"], 0)

    def test_result_contains_all_keys(self) -> None:
        """Result dict always contains all expected keys."""
        result = self.service.analyze(make_employee(), make_requirement())
        for key in ("total_projects", "lead_projects", "required_projects",
                    "required_lead_projects", "remaining_projects", "remaining_lead_projects"):
            self.assertIn(key, result)

    def test_lead_project_count_is_accurate(self) -> None:
        """lead_projects count reflects only projects with lead_project=True."""
        projects = [
            self._make_project("P1", lead=True),
            self._make_project("P2", lead=False),
            self._make_project("P3", lead=True),
        ]
        result = self.service.analyze(make_employee(projects=projects), make_requirement())
        self.assertEqual(result["lead_projects"], 2)


# ---------------------------------------------------------------------------
# GapAnalysisService
# ---------------------------------------------------------------------------

class TestGapAnalysisService(unittest.TestCase):
    """Tests for GapAnalysisService using a mocked DataLoader."""

    def _make_service(self, employee, requirement) -> GapAnalysisService:
        """Build a GapAnalysisService with a mocked DataLoader."""
        service = GapAnalysisService.__new__(GapAnalysisService)
        mock_loader = MagicMock()
        mock_loader.load_employee.return_value = employee
        mock_loader.load_grade_requirement.return_value = requirement
        service._loader = mock_loader
        service._skill_svc = SkillGapService()
        service._cert_svc = CertificationGapService()
        service._exp_svc = ExperienceGapService()
        service._proj_svc = ProjectGapService()
        return service

    def test_employee_not_found_raises(self) -> None:
        """EmployeeNotFoundError raised when employee does not exist."""
        service = self._make_service(None, None)
        with self.assertRaises(EmployeeNotFoundError):
            service.run(999)

    def test_grade_not_found_raises(self) -> None:
        """GradeNotFoundError raised when target grade has no requirement record."""
        service = self._make_service(make_employee(), None)
        with self.assertRaises(GradeNotFoundError):
            service.run(1)

    def test_full_analysis_returns_all_keys(self) -> None:
        """run() returns a dict with all expected top-level keys."""
        service = self._make_service(make_employee(), make_requirement())
        result = service.run(1)
        for key in ("employee", "requirement", "skill_gaps",
                    "certification_gaps", "experience_gap", "project_gap"):
            self.assertIn(key, result)

    def test_run_returns_correct_employee(self) -> None:
        """run() result contains the same employee object that was loaded."""
        emp = make_employee(employee_id=42)
        service = self._make_service(emp, make_requirement())
        result = service.run(42)
        self.assertEqual(result["employee"].employee_id, 42)

    def test_run_with_all_gaps(self) -> None:
        """run() correctly delegates to all four gap services."""
        employee = make_employee(
            experience_years=1.0,
            skills=[EmployeeSkill("Java", "Backend", 2)],
            certifications=[],
            projects=[],
        )
        requirement = make_requirement(
            skills=[GradeSkillRequirement("Java", "Backend", 5, 1.0, True)],
            certifications=[GradeCertificationRequirement("AWS-CCP", "Amazon", True)],
        )
        service = self._make_service(employee, requirement)
        result = service.run(1)
        self.assertEqual(len(result["skill_gaps"]), 1)
        self.assertEqual(len(result["certification_gaps"]), 1)
        self.assertGreater(result["experience_gap"]["remaining_years"], 0)
        self.assertGreater(result["project_gap"]["remaining_projects"], 0)

    def test_run_with_no_gaps(self) -> None:
        """run() returns empty gap lists when employee meets all requirements."""
        employee = make_employee(
            experience_years=6.0,
            skills=[EmployeeSkill("Java", "Backend", 5)],
            certifications=[
                EmployeeCertification("AWS-CCP", "Amazon", "Completed", "2023-01-01", None)
            ],
            projects=[
                EmployeeProject(f"P{i}", "Java", "Hard", "Cloud", "Lead", True, 6, 5.0)
                for i in range(3)
            ],
        )
        requirement = make_requirement(
            skills=[GradeSkillRequirement("Java", "Backend", 5, 1.0, True)],
            certifications=[GradeCertificationRequirement("AWS-CCP", "Amazon", True)],
        )
        service = self._make_service(employee, requirement)
        result = service.run(1)
        self.assertEqual(result["skill_gaps"], [])
        self.assertEqual(result["certification_gaps"], [])
        self.assertEqual(result["experience_gap"]["remaining_years"], 0.0)
        self.assertEqual(result["project_gap"]["remaining_projects"], 0)


# ---------------------------------------------------------------------------
# JsonBuilder
# ---------------------------------------------------------------------------

class TestJsonBuilder(unittest.TestCase):
    """Tests for JsonBuilder."""

    def setUp(self) -> None:
        self.builder = JsonBuilder()

    def _make_analysis(self, **overrides) -> dict:
        """Return a base analysis dict."""
        base = {
            "employee": make_employee(),
            "requirement": make_requirement(),
            "skill_gaps": [],
            "certification_gaps": [],
            "experience_gap": {
                "current_years": 3.0,
                "required_years": 5.0,
                "remaining_years": 2.0,
            },
            "project_gap": {
                "total_projects": 1,
                "lead_projects": 0,
                "required_projects": 3,
                "required_lead_projects": 1,
                "remaining_projects": 2,
                "remaining_lead_projects": 1,
            },
        }
        base.update(overrides)
        return base

    def test_report_top_level_structure(self) -> None:
        """build() returns a dict with 'employee' and 'gapAnalysis' keys."""
        report = self.builder.build(self._make_analysis())
        self.assertIn("employee", report)
        self.assertIn("gapAnalysis", report)

    def test_gap_analysis_section_keys(self) -> None:
        """gapAnalysis section contains skills, certifications, experience, projects."""
        report = self.builder.build(self._make_analysis())
        for key in ("skills", "certifications", "experience", "projects"):
            self.assertIn(key, report["gapAnalysis"])

    def test_employee_fields_present(self) -> None:
        """Employee section contains all expected fields."""
        report = self.builder.build(self._make_analysis())
        for field_name in (
            "employee_id", "employee_code", "full_name", "email",
            "department", "current_grade", "target_grade",
        ):
            self.assertIn(field_name, report["employee"])

    def test_skill_gaps_formatted_correctly(self) -> None:
        """Skill gaps are formatted with all required keys."""
        analysis = self._make_analysis(skill_gaps=[{
            "skill": "Java", "category": "Backend",
            "current_level": 3, "required_level": 5, "gap": 2, "mandatory": True,
        }])
        report = self.builder.build(analysis)
        skill = report["gapAnalysis"]["skills"][0]
        for key in ("skill", "category", "current_level", "required_level", "gap", "mandatory"):
            self.assertIn(key, skill)
        self.assertEqual(skill["gap"], 2)

    def test_certification_gaps_formatted_correctly(self) -> None:
        """Certification gaps are formatted with all required keys."""
        analysis = self._make_analysis(certification_gaps=[{
            "certification": "AWS-CCP", "provider": "Amazon", "mandatory": True,
        }])
        report = self.builder.build(analysis)
        cert = report["gapAnalysis"]["certifications"][0]
        for key in ("certification", "provider", "mandatory"):
            self.assertIn(key, cert)

    def test_experience_gap_formatted_correctly(self) -> None:
        """Experience gap section contains current, required, and remaining years."""
        report = self.builder.build(self._make_analysis())
        exp = report["gapAnalysis"]["experience"]
        self.assertEqual(exp["current_years"], 3.0)
        self.assertEqual(exp["required_years"], 5.0)
        self.assertEqual(exp["remaining_years"], 2.0)

    def test_project_gap_formatted_correctly(self) -> None:
        """Project gap section contains all six expected fields."""
        report = self.builder.build(self._make_analysis())
        proj = report["gapAnalysis"]["projects"]
        for key in ("total_projects", "lead_projects", "required_projects",
                    "required_lead_projects", "remaining_projects", "remaining_lead_projects"):
            self.assertIn(key, proj)

    def test_empty_gaps_produce_empty_lists(self) -> None:
        """Empty skill and certification gaps produce empty lists in the report."""
        report = self.builder.build(self._make_analysis())
        self.assertEqual(report["gapAnalysis"]["skills"], [])
        self.assertEqual(report["gapAnalysis"]["certifications"], [])

    def test_employee_values_match_model(self) -> None:
        """Employee section values match the Employee model fields."""
        emp = make_employee(employee_id=7, full_name="Bob Jones", department="Cloud")
        report = self.builder.build(self._make_analysis(employee=emp))
        self.assertEqual(report["employee"]["employee_id"], 7)
        self.assertEqual(report["employee"]["full_name"], "Bob Jones")
        self.assertEqual(report["employee"]["department"], "Cloud")


if __name__ == "__main__":
    unittest.main()
