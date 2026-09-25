"""
Skill Decay & Recency Weighting Service — Phase 1.1

Calculates skill recency factors and decayed effective skill levels based on time elapsed
since a skill was last used or updated.

Rules:
- Grace Period: 6 months (skills used within 6 months have recency_factor = 1.0).
- Decay Formula: Exponential decay with a 24-month half-life for inactivity beyond grace period.
- Minimum Recency Factor: 0.3 (skills retain at least 30% of nominal rating).
- Effective Skill Level = round(nominal_level * recency_factor, 2).
"""

import math
import logging
from datetime import datetime, date
from typing import Optional, Union

from models.employee import Employee, EmployeeSkill

logger = logging.getLogger(__name__)

# Constants for skill decay calculation
GRACE_PERIOD_MONTHS: int = 6
HALF_LIFE_MONTHS: float = 24.0
MIN_RECENCY_FACTOR: float = 0.3
LAMBDA_DECAY: float = math.log(2) / HALF_LIFE_MONTHS  # ~0.02888 per month


class SkillDecayService:
    """Service to evaluate skill recency decay and compute effective skill levels."""

    @staticmethod
    def parse_date(date_val: Optional[Union[str, date]]) -> Optional[date]:
        """Parse string or date into datetime.date object."""
        if not date_val:
            return None
        if isinstance(date_val, date):
            return date_val
        try:
            return datetime.strptime(str(date_val).split("T")[0], "%Y-%m-%d").date()
        except ValueError:
            logger.warning("Could not parse date string '%s'", date_val)
            return None

    def calculate_recency_factor(
        self,
        last_used_date: Optional[Union[str, date]],
        reference_date: Optional[Union[str, date]] = None,
    ) -> float:
        """
        Calculate recency factor in range [0.3, 1.0].

        Args:
            last_used_date: Date skill was last used/updated.
            reference_date: Reference evaluation date (defaults to today).

        Returns:
            float recency factor rounded to 3 decimal places.
        """
        if not last_used_date:
            # Default to no decay for missing date
            return 1.0

        parsed_last_used = self.parse_date(last_used_date)
        if not parsed_last_used:
            return 1.0

        parsed_ref = self.parse_date(reference_date) if reference_date else date.today()

        if parsed_last_used >= parsed_ref:
            return 1.0

        # Calculate difference in months
        days_diff = (parsed_ref - parsed_last_used).days
        months_inactive = days_diff / 30.4375

        if months_inactive <= GRACE_PERIOD_MONTHS:
            return 1.0

        decay_months = months_inactive - GRACE_PERIOD_MONTHS
        factor = math.exp(-LAMBDA_DECAY * decay_months)
        factor = max(MIN_RECENCY_FACTOR, factor)

        return round(factor, 3)

    def get_freshness_status(self, recency_factor: float) -> str:
        """Categorise skill freshness based on recency factor."""
        if recency_factor >= 0.9:
            return "Active"
        elif recency_factor >= 0.65:
            return "Needs Refresh"
        else:
            return "Stale"

    def apply_decay_to_skill(
        self,
        skill: EmployeeSkill,
        reference_date: Optional[Union[str, date]] = None,
    ) -> EmployeeSkill:
        """Apply recency factor and effective skill level to a single EmployeeSkill."""
        factor = self.calculate_recency_factor(skill.last_used_date, reference_date)
        skill.recency_factor = factor
        skill.effective_skill_level = round(skill.skill_level * factor, 2)
        return skill

    def apply_decay_to_employee(
        self,
        employee: Employee,
        reference_date: Optional[Union[str, date]] = None,
    ) -> Employee:
        """
        Apply skill decay to all skills of an employee profile.

        Args:
            employee: Employee object.
            reference_date: Optional reference date.

        Returns:
            Employee object with updated skills.
        """
        for skill in employee.skills:
            self.apply_decay_to_skill(skill, reference_date)

        logger.info(
            "Skill decay applied to employee %s (%d skills).",
            employee.employee_id,
            len(employee.skills),
        )
        return employee
