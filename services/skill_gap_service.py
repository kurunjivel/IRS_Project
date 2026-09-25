"""
Skill gap service.

Compares an employee's current skills and levels against
the skill requirements of the target grade.
"""

import logging

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class SkillGapService:
    """Identifies missing skills and insufficient skill levels."""

    def __init__(self) -> None:
        from services.skill_decay_service import SkillDecayService
        from services.semantic.semantic_matcher import SemanticMatcher
        self._decay_svc = SkillDecayService()
        self._matcher = SemanticMatcher()

    def analyze(self, employee: Employee, requirement: GradeRequirement) -> list[dict]:
        """
        Compare employee skills against grade skill requirements.

        For each required skill:
        - If the employee does not have it at all, current_level is 0.
        - If the employee has it but below the required level, the gap is calculated.
        - If the employee meets or exceeds the required level, it is excluded.

        Args:
            employee:    The loaded Employee object.
            requirement: The loaded GradeRequirement object.

        Returns:
            List of dicts, one per skill gap
        """
        employee_skill_map: dict[str, EmployeeSkill] = {
            s.skill_name.lower(): s
            for s in employee.skills
        }

        gaps: list[dict] = []

        decay_svc = self._decay_svc
        matcher = self._matcher

        # Build list of employee skill dicts for semantic matcher
        emp_skill_dicts = [
            {
                "skill_name": s.skill_name,
                "skill_level": s.skill_level,
                "effective_level": s.effective_skill_level if s.effective_skill_level > 0 else float(s.skill_level),
            }
            for s in employee.skills
        ]

        for req in requirement.skills:
            match_res = matcher.match_skill(req.skill_name, float(req.required_level), emp_skill_dicts)

            emp_skill = employee_skill_map.get(req.skill_name.lower())
            if emp_skill:
                nominal_level = emp_skill.skill_level
                effective_level = emp_skill.effective_skill_level if emp_skill.effective_skill_level > 0 else float(emp_skill.skill_level)
                recency_factor = emp_skill.recency_factor
                last_used_date = emp_skill.last_used_date
            elif match_res.matched_employee_skill and match_res.match_type in ("STRONG_SEMANTIC_MATCH", "RELATED_SKILL", "PARTIAL_RELEVANCE"):
                nominal_level = 0
                effective_level = match_res.effective_matched_level
                recency_factor = 1.0
                last_used_date = None
            else:
                nominal_level = 0
                effective_level = 0.0
                recency_factor = 1.0
                last_used_date = None

            gap = req.required_level - effective_level

            if gap > 0:
                freshness = decay_svc.get_freshness_status(recency_factor)
                gaps.append({
                    "skill": req.skill_name,
                    "category": req.category,
                    "current_level": nominal_level,
                    "effective_level": round(effective_level, 2),
                    "required_level": req.required_level,
                    "gap": round(gap, 2),
                    "mandatory": req.mandatory,
                    "recency_factor": recency_factor,
                    "last_used_date": last_used_date,
                    "freshness_status": freshness,
                    # Extended Phase 7 Semantic Skill Matching Attributes
                    "matched_employee_skill": match_res.matched_employee_skill,
                    "match_type": match_res.match_type,
                    "similarity_score": match_res.similarity_score,
                    "effective_matched_level": match_res.effective_matched_level,
                    "gap_severity": match_res.gap_severity,
                })

        logger.info(
            "Skill gap analysis for employee %s: %d gap(s) found.",
            employee.employee_id,
            len(gaps),
        )
        return gaps
