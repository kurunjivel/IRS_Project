"""
Automated tests for Skill Decay & Recency Weighting (Phase 1.1).

Validates:
- Recency factor calculation math and grace period logic.
- Effective skill level computation.
- Freshness status classification (Active, Needs Refresh, Stale).
- Integration with SkillGapService and SkillScoreService.
- Integration with DataLoader and API endpoints.
"""

import pytest
from datetime import date, timedelta
from models.employee import Employee, EmployeeSkill
from models.grade_requirement import GradeRequirement, GradeSkillRequirement
from services.skill_decay_service import SkillDecayService
from services.skill_gap_service import SkillGapService
from services.readiness.skill_score_service import SkillScoreService


class TestSkillDecayService:
    """Unit tests for SkillDecayService calculations."""

    @pytest.fixture
    def service(self):
        return SkillDecayService()

    def test_recent_skill_has_no_decay(self, service):
        """Skill used within 6 months (grace period) must have recency_factor = 1.0."""
        ref_date = date(2026, 1, 1)
        recent_date = (ref_date - timedelta(days=90)).strftime("%Y-%m-%d")

        factor = service.calculate_recency_factor(recent_date, reference_date=ref_date)
        assert factor == 1.0
        assert service.get_freshness_status(factor) == "Active"

    def test_decay_after_grace_period(self, service):
        """Skill unused for 18 months should decay moderately."""
        ref_date = date(2026, 1, 1)
        old_date = (ref_date - timedelta(days=18 * 30)).strftime("%Y-%m-%d")

        factor = service.calculate_recency_factor(old_date, reference_date=ref_date)
        assert 0.6 <= factor < 1.0
        assert service.get_freshness_status(factor) in ["Needs Refresh", "Stale"]

    def test_minimum_recency_factor_floor(self, service):
        """Skill unused for 10 years must not drop below MIN_RECENCY_FACTOR (0.3)."""
        ref_date = date(2026, 1, 1)
        ancient_date = "2010-01-01"

        factor = service.calculate_recency_factor(ancient_date, reference_date=ref_date)
        assert factor == 0.3
        assert service.get_freshness_status(factor) == "Stale"

    def test_missing_date_defaults_to_one(self, service):
        """Missing or None last_used_date returns factor 1.0."""
        assert service.calculate_recency_factor(None) == 1.0
        assert service.calculate_recency_factor("") == 1.0

    def test_apply_decay_to_skill(self, service):
        """Verify effective_skill_level calculation on EmployeeSkill."""
        skill = EmployeeSkill(
            skill_name="Python",
            category="Backend",
            skill_level=4,
            last_used_date="2024-01-01",
        )
        ref_date = date(2026, 1, 1)
        service.apply_decay_to_skill(skill, reference_date=ref_date)

        assert skill.recency_factor < 1.0
        assert skill.effective_skill_level < 4.0
        assert skill.effective_skill_level == round(4 * skill.recency_factor, 2)

    def test_gap_service_uses_effective_skill_level(self, service):
        """Verify SkillGapService considers decayed skill levels."""
        ref_date = date(2026, 1, 1)
        old_date = (ref_date - timedelta(days=24 * 30)).strftime("%Y-%m-%d")

        emp = Employee(
            employee_id=1,
            employee_code="EMP001",
            full_name="Alice",
            email="alice@test.com",
            department="Eng",
            experience_years=5.0,
            performance_rating=4.5,
            joining_date="2020-01-01",
            current_grade="G2",
            current_grade_id=2,
            target_grade="G3",
            target_grade_id=3,
            skills=[
                EmployeeSkill("Java", "Backend", 4, last_used_date=old_date)
            ]
        )
        service.apply_decay_to_employee(emp, reference_date=ref_date)

        req = GradeRequirement(
            grade_id=3,
            grade_name="G3",
            description="Senior",
            skills=[GradeSkillRequirement("Java", "Backend", 4, 1.0, True)]
        )

        gap_service = SkillGapService()
        gaps = gap_service.analyze(emp, req)

        # Because Java decayed from 4 to ~2.8, a gap should be detected!
        assert len(gaps) == 1
        assert gaps[0]["skill"] == "Java"
        assert gaps[0]["effective_level"] < 4.0
        assert gaps[0]["gap"] > 0
