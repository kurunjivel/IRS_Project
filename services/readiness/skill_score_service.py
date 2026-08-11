"""
Skill Score Service — Phase 3.

Calculates the skill component of the promotion readiness score
from the gap analysis output produced by Phase 2.
"""

import logging
from dataclasses import dataclass

from models.grade_requirement import GradeRequirement
from models.employee import Employee

logger = logging.getLogger(__name__)

# Skills contribute 40 points to the overall 100-point readiness score.
SKILL_MAX_SCORE: float = 40.0


@dataclass
class SkillScoreResult:
    """Result of the skill scoring calculation."""

    score: float
    max_score: float
    percentage: float
    missing_skills: list[str]


class SkillScoreService:
    """
    Scores an employee's skills against the target grade requirements.

    Rules:
    - Missing skill          → 0 points for that skill slot.
    - Skill level too low    → proportional points (current / required).
    - Skill level meets/exceeds requirement → full points for that slot.
    """

    def calculate(
        self,
        employee: Employee,
        requirement: GradeRequirement,
        skill_gaps: list[dict],
    ) -> SkillScoreResult:
        """
        Calculate the skill readiness score.

        Args:
            employee:    The loaded Employee object (used for its skill list).
            requirement: The loaded GradeRequirement object.
            skill_gaps:  The skill_gaps list produced by Phase 2 SkillGapService.

        Returns:
            SkillScoreResult with score, max_score, percentage, and missing_skills.
        """
        if not requirement.skills:
            logger.info("No skill requirements defined — awarding full skill score.")
            return SkillScoreResult(
                score=SKILL_MAX_SCORE,
                max_score=SKILL_MAX_SCORE,
                percentage=100.0,
                missing_skills=[],
            )

        # Build a lookup of gaps keyed by lowercase skill name for O(1) access.
        gap_map: dict[str, dict] = {
            g["skill"].lower(): g for g in skill_gaps
        }

        points_per_skill = SKILL_MAX_SCORE / len(requirement.skills)
        earned = 0.0
        missing_skills: list[str] = []

        for req in requirement.skills:
            key = req.skill_name.lower()
            if key not in gap_map:
                # Employee meets or exceeds this skill requirement.
                earned += points_per_skill
            else:
                gap = gap_map[key]
                current = gap["current_level"]
                required = gap["required_level"]

                if current == 0:
                    # Skill is entirely missing.
                    missing_skills.append(req.skill_name)
                else:
                    # Partial credit: proportional to level achieved.
                    earned += points_per_skill * (current / required)

        score = round(earned, 2)
        percentage = round((score / SKILL_MAX_SCORE) * 100, 2)

        logger.info(
            "Skill score for employee %s: %.2f / %.2f (%.2f%%)",
            employee.employee_id,
            score,
            SKILL_MAX_SCORE,
            percentage,
        )

        return SkillScoreResult(
            score=score,
            max_score=SKILL_MAX_SCORE,
            percentage=percentage,
            missing_skills=missing_skills,
        )
