"""
Unit tests for the IRS Phase 3 Readiness Scoring Engine.

All tests use in-memory Employee / GradeRequirement objects —
no live database or mysql.connector required.

Test cases:
    1. Employee fully eligible
    2. Employee missing one skill
    3. Employee missing certifications
    4. Employee missing experience
    5. Employee missing projects
    6. Employee with poor performance
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
from services.readiness.skill_score_service import SkillScoreService, SKILL_MAX_SCORE
from services.readiness.certification_score_service import (
    CertificationScoreService,
    CERTIFICATION_MAX_SCORE,
)
from services.readiness.experience_score_service import (
    ExperienceScoreService,
    EXPERIENCE_MAX_SCORE,
)
from services.readiness.project_score_service import ProjectScoreService, PROJECT_MAX_SCORE
from services.readiness.performance_score_service import (
    PerformanceScoreService,
    PERFORMANCE_MAX_SCORE,
)
from services.readiness.readiness_engine import ReadinessEngine
from services.readiness.readiness_report import ReadinessReportBuilder


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_employee(**overrides) -> Employee:
    defaults = dict(
        employee_id=1,
        employee_code="EMP001",
        full_name="Alice Smith",
        email="alice@example.com",
        department="Engineering",
        experience_years=5.0,
        performance_rating=5.0,
        joining_date="2019-01-01",
        current_grade="Grade B",
        current_grade_id=2,
        target_grade="Grade A",
        target_grade_id=1,
        skills=[
            EmployeeSkill("Python", "Backend", 5),
            EmployeeSkill("AWS", "Cloud", 4),
        ],
        certifications=[
            EmployeeCertification("AWS-CCP", "Amazon", "Completed", "2023-01-01", None),
        ],
        projects=[
            EmployeeProject("Project Alpha", "Python", "High", "Finance", "Lead", True, 6, 4.5),
            EmployeeProject("Project Beta", "AWS", "Medium", "HR", "Developer", False, 4, 4.0),
            EmployeeProject("Project Gamma", "Java", "Low", "IT", "Developer", False, 3, 3.5),
        ],
    )
    defaults.update(overrides)
    return Employee(**defaults)


def _make_requirement(**overrides) -> GradeRequirement:
    defaults = dict(
        grade_id=1,
        grade_name="Grade A",
        description="Senior level",
        skills=[
            GradeSkillRequirement("Python", "Backend", 5, 1.0, True),
            GradeSkillRequirement("AWS", "Cloud", 4, 0.8, False),
        ],
        certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
        ],
        project_requirement=GradeProjectRequirement(
            minimum_projects=3,
            minimum_lead_projects=1,
            minimum_experience=5.0,
        ),
    )
    defaults.update(overrides)
    return GradeRequirement(**defaults)


def _make_gap_analysis(employee: Employee, requirement: GradeRequirement) -> dict:
    """Build a gap_analysis dict the same way GapAnalysisService.run() would."""
    from services.skill_gap_service import SkillGapService
    from services.certification_gap_service import CertificationGapService
    from services.experience_gap_service import ExperienceGapService
    from services.project_gap_service import ProjectGapService

    return {
        "employee": employee,
        "requirement": requirement,
        "skill_gaps": SkillGapService().analyze(employee, requirement),
        "certification_gaps": CertificationGapService().analyze(employee, requirement),
        "experience_gap": ExperienceGapService().analyze(employee, requirement),
        "project_gap": ProjectGapService().analyze(employee, requirement),
    }


# ---------------------------------------------------------------------------
# SkillScoreService
# ---------------------------------------------------------------------------

class TestSkillScoreService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = SkillScoreService()

    def test_full_score_when_all_skills_met(self) -> None:
        employee = _make_employee()
        requirement = _make_requirement()
        result = self.service.calculate(employee, requirement, [])
        self.assertAlmostEqual(result.score, SKILL_MAX_SCORE)
        self.assertEqual(result.missing_skills, [])

    def test_zero_score_for_missing_skill(self) -> None:
        employee = _make_employee(skills=[])
        requirement = _make_requirement(skills=[
            GradeSkillRequirement("Python", "Backend", 5, 1.0, True),
        ])
        gaps = [{"skill": "Python", "category": "Backend", "current_level": 0,
                 "required_level": 5, "gap": 5, "mandatory": True}]
        result = self.service.calculate(employee, requirement, gaps)
        self.assertAlmostEqual(result.score, 0.0)
        self.assertIn("Python", result.missing_skills)

    def test_partial_score_for_low_skill_level(self) -> None:
        employee = _make_employee(skills=[EmployeeSkill("Python", "Backend", 3)])
        requirement = _make_requirement(skills=[
            GradeSkillRequirement("Python", "Backend", 5, 1.0, True),
        ])
        gaps = [{"skill": "Python", "category": "Backend", "current_level": 3,
                 "required_level": 5, "gap": 2, "mandatory": True}]
        result = self.service.calculate(employee, requirement, gaps)
        expected = SKILL_MAX_SCORE * (3 / 5)
        self.assertAlmostEqual(result.score, round(expected, 2))
        self.assertEqual(result.missing_skills, [])

    def test_full_score_when_no_requirements(self) -> None:
        employee = _make_employee()
        requirement = _make_requirement(skills=[])
        result = self.service.calculate(employee, requirement, [])
        self.assertAlmostEqual(result.score, SKILL_MAX_SCORE)


# ---------------------------------------------------------------------------
# CertificationScoreService
# ---------------------------------------------------------------------------

class TestCertificationScoreService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = CertificationScoreService()

    def test_full_score_when_all_certs_held(self) -> None:
        employee = _make_employee()
        requirement = _make_requirement()
        result = self.service.calculate(employee, requirement, [])
        self.assertAlmostEqual(result.score, CERTIFICATION_MAX_SCORE)
        self.assertEqual(result.missing, [])

    def test_zero_score_when_cert_missing(self) -> None:
        employee = _make_employee(certifications=[])
        requirement = _make_requirement()
        gaps = [{"certification": "AWS-CCP", "provider": "Amazon", "mandatory": True}]
        result = self.service.calculate(employee, requirement, gaps)
        self.assertAlmostEqual(result.score, 0.0)
        self.assertIn("AWS-CCP", result.missing)

    def test_partial_score_for_partial_certs(self) -> None:
        requirement = _make_requirement(certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
            GradeCertificationRequirement("AZ-900", "Microsoft", False),
        ])
        employee = _make_employee()
        gaps = [{"certification": "AZ-900", "provider": "Microsoft", "mandatory": False}]
        result = self.service.calculate(employee, requirement, gaps)
        self.assertAlmostEqual(result.score, CERTIFICATION_MAX_SCORE / 2)
        self.assertEqual(result.completed, 1)


# ---------------------------------------------------------------------------
# ExperienceScoreService
# ---------------------------------------------------------------------------

class TestExperienceScoreService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = ExperienceScoreService()

    def test_full_score_when_experience_met(self) -> None:
        employee = _make_employee(experience_years=5.0)
        exp_gap = {"current_years": 5.0, "required_years": 5.0, "remaining_years": 0.0}
        result = self.service.calculate(employee, exp_gap)
        self.assertAlmostEqual(result.score, EXPERIENCE_MAX_SCORE)

    def test_partial_score_when_experience_short(self) -> None:
        employee = _make_employee(experience_years=2.5)
        exp_gap = {"current_years": 2.5, "required_years": 5.0, "remaining_years": 2.5}
        result = self.service.calculate(employee, exp_gap)
        self.assertAlmostEqual(result.score, round(EXPERIENCE_MAX_SCORE * 0.5, 2))

    def test_score_capped_when_experience_exceeds_requirement(self) -> None:
        employee = _make_employee(experience_years=10.0)
        exp_gap = {"current_years": 10.0, "required_years": 5.0, "remaining_years": 0.0}
        result = self.service.calculate(employee, exp_gap)
        self.assertAlmostEqual(result.score, EXPERIENCE_MAX_SCORE)


# ---------------------------------------------------------------------------
# ProjectScoreService
# ---------------------------------------------------------------------------

class TestProjectScoreService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = ProjectScoreService()

    def test_full_score_when_projects_met(self) -> None:
        employee = _make_employee()
        proj_gap = {
            "total_projects": 3, "lead_projects": 1,
            "required_projects": 3, "required_lead_projects": 1,
            "remaining_projects": 0, "remaining_lead_projects": 0,
        }
        result = self.service.calculate(employee, proj_gap)
        self.assertAlmostEqual(result.score, PROJECT_MAX_SCORE)

    def test_zero_score_when_no_projects(self) -> None:
        employee = _make_employee(projects=[])
        proj_gap = {
            "total_projects": 0, "lead_projects": 0,
            "required_projects": 3, "required_lead_projects": 1,
            "remaining_projects": 3, "remaining_lead_projects": 1,
        }
        result = self.service.calculate(employee, proj_gap)
        self.assertAlmostEqual(result.score, 0.0)

    def test_partial_score_for_partial_projects(self) -> None:
        employee = _make_employee()
        proj_gap = {
            "total_projects": 2, "lead_projects": 0,
            "required_projects": 4, "required_lead_projects": 2,
            "remaining_projects": 2, "remaining_lead_projects": 2,
        }
        result = self.service.calculate(employee, proj_gap)
        self.assertGreater(result.score, 0.0)
        self.assertLess(result.score, PROJECT_MAX_SCORE)


# ---------------------------------------------------------------------------
# PerformanceScoreService
# ---------------------------------------------------------------------------

class TestPerformanceScoreService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = PerformanceScoreService()

    def test_full_score_for_max_rating(self) -> None:
        employee = _make_employee(performance_rating=5.0)
        result = self.service.calculate(employee)
        self.assertAlmostEqual(result.score, PERFORMANCE_MAX_SCORE)

    def test_zero_score_for_zero_rating(self) -> None:
        employee = _make_employee(performance_rating=0.0)
        result = self.service.calculate(employee)
        self.assertAlmostEqual(result.score, 0.0)

    def test_proportional_score(self) -> None:
        employee = _make_employee(performance_rating=2.5)
        result = self.service.calculate(employee)
        self.assertAlmostEqual(result.score, round(PERFORMANCE_MAX_SCORE * 0.5, 2))


# ---------------------------------------------------------------------------
# ReadinessEngine — integration-style tests
# ---------------------------------------------------------------------------

class TestReadinessEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = ReadinessEngine()
        self.report_builder = ReadinessReportBuilder()

    # 1. Employee fully eligible
    def test_fully_eligible_employee(self) -> None:
        employee = _make_employee()
        requirement = _make_requirement()
        gap = _make_gap_analysis(employee, requirement)
        result = self.engine.calculate(gap)
        self.assertAlmostEqual(result.readiness_score, 100.0)
        report = self.report_builder.build(employee, result)
        self.assertEqual(report.readiness_level, "Promotion Ready")
        self.assertEqual(report.promotion_decision, "Ready")

    # 2. Employee missing one skill
    def test_missing_one_skill(self) -> None:
        employee = _make_employee(skills=[EmployeeSkill("Python", "Backend", 5)])
        requirement = _make_requirement()
        gap = _make_gap_analysis(employee, requirement)
        result = self.engine.calculate(gap)
        self.assertLess(result.readiness_score, 100.0)
        self.assertGreater(result.breakdown.skills.score, 0.0)

    # 3. Employee missing certifications
    def test_missing_certifications(self) -> None:
        employee = _make_employee(certifications=[])
        requirement = _make_requirement()
        gap = _make_gap_analysis(employee, requirement)
        result = self.engine.calculate(gap)
        self.assertAlmostEqual(result.breakdown.certifications.score, 0.0)
        self.assertLess(result.readiness_score, 100.0)

    # 4. Employee missing experience
    def test_missing_experience(self) -> None:
        employee = _make_employee(experience_years=1.0)
        requirement = _make_requirement()
        gap = _make_gap_analysis(employee, requirement)
        result = self.engine.calculate(gap)
        self.assertLess(result.breakdown.experience.score, EXPERIENCE_MAX_SCORE)
        self.assertLess(result.readiness_score, 100.0)

    # 5. Employee missing projects
    def test_missing_projects(self) -> None:
        employee = _make_employee(projects=[])
        requirement = _make_requirement()
        gap = _make_gap_analysis(employee, requirement)
        result = self.engine.calculate(gap)
        self.assertAlmostEqual(result.breakdown.projects.score, 0.0)
        self.assertLess(result.readiness_score, 100.0)

    # 6. Employee with poor performance
    def test_poor_performance(self) -> None:
        employee = _make_employee(performance_rating=1.0)
        requirement = _make_requirement()
        gap = _make_gap_analysis(employee, requirement)
        result = self.engine.calculate(gap)
        self.assertLess(result.breakdown.performance.score, PERFORMANCE_MAX_SCORE)
        report = self.report_builder.build(employee, result)
        # Poor performance alone should not block promotion if everything else is fine
        self.assertIn(
            report.promotion_decision,
            ("Ready", "Conditional"),
        )


# ---------------------------------------------------------------------------
# ReadinessReportBuilder — level and decision mapping
# ---------------------------------------------------------------------------

class TestReadinessReportBuilder(unittest.TestCase):

    def setUp(self) -> None:
        self.builder = ReadinessReportBuilder()
        self.employee = _make_employee()

    def _result_with_score(self, score: float):
        """Build a minimal ReadinessResult with a given overall score."""
        from services.readiness.readiness_engine import ReadinessResult, ReadinessBreakdown
        from services.readiness.skill_score_service import SkillScoreResult
        from services.readiness.certification_score_service import CertificationScoreResult
        from services.readiness.experience_score_service import ExperienceScoreResult
        from services.readiness.project_score_service import ProjectScoreResult
        from services.readiness.performance_score_service import PerformanceScoreResult

        return ReadinessResult(
            readiness_score=score,
            breakdown=ReadinessBreakdown(
                skills=SkillScoreResult(score=score, max_score=40.0, percentage=100.0, missing_skills=[]),
                certifications=CertificationScoreResult(score=0.0, max_score=15.0, completed=0, missing=[]),
                experience=ExperienceScoreResult(current_years=5.0, required_years=5.0, gap_years=0.0, score=0.0),
                projects=ProjectScoreResult(completed=3, required=3, remaining=0, lead_completed=1,
                                            lead_required=1, lead_remaining=0, score=0.0),
                performance=PerformanceScoreResult(performance_rating=5.0, score=0.0),
            ),
        )

    def test_level_promotion_ready(self) -> None:
        report = self.builder.build(self.employee, self._result_with_score(95.0))
        self.assertEqual(report.readiness_level, "Promotion Ready")
        self.assertEqual(report.promotion_decision, "Ready")

    def test_level_almost_ready(self) -> None:
        report = self.builder.build(self.employee, self._result_with_score(80.0))
        self.assertEqual(report.readiness_level, "Almost Ready")
        self.assertEqual(report.promotion_decision, "Conditional")

    def test_level_needs_improvement(self) -> None:
        report = self.builder.build(self.employee, self._result_with_score(65.0))
        self.assertEqual(report.readiness_level, "Needs Improvement")
        self.assertEqual(report.promotion_decision, "Conditional")

    def test_level_significant_gaps(self) -> None:
        report = self.builder.build(self.employee, self._result_with_score(50.0))
        self.assertEqual(report.readiness_level, "Significant Gaps")
        self.assertEqual(report.promotion_decision, "Not Ready")

    def test_level_not_ready(self) -> None:
        report = self.builder.build(self.employee, self._result_with_score(20.0))
        self.assertEqual(report.readiness_level, "Not Ready")
        self.assertEqual(report.promotion_decision, "Not Ready")


if __name__ == "__main__":
    unittest.main()
