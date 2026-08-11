"""
Project Score Service — Phase 3.

Calculates the project component of the promotion readiness score
from the gap analysis output produced by Phase 2.
"""

import logging
from dataclasses import dataclass

from models.employee import Employee

logger = logging.getLogger(__name__)

# Projects contribute 20 points to the overall 100-point readiness score.
PROJECT_MAX_SCORE: float = 20.0

# Split: 70% for total projects, 30% for lead projects.
_TOTAL_WEIGHT: float = 0.70
_LEAD_WEIGHT: float = 0.30


@dataclass
class ProjectScoreResult:
    """Result of the project scoring calculation."""

    completed: int
    required: int
    remaining: int
    lead_completed: int
    lead_required: int
    lead_remaining: int
    score: float


class ProjectScoreService:
    """
    Scores an employee's project participation against the target grade requirements.

    Score is split between total project count (70%) and lead project count (30%).
    Each sub-score is capped at its respective maximum — exceeding requirements
    does not yield bonus points.
    """

    def calculate(
        self,
        employee: Employee,
        project_gap: dict,
    ) -> ProjectScoreResult:
        """
        Calculate the project readiness score.

        Args:
            employee:     The loaded Employee object.
            project_gap:  The project_gap dict produced by Phase 2
                          ProjectGapService (keys: total_projects, lead_projects,
                          required_projects, required_lead_projects,
                          remaining_projects, remaining_lead_projects).

        Returns:
            ProjectScoreResult with counts and score.
        """
        total_done: int = project_gap["total_projects"]
        total_req: int = project_gap["required_projects"]
        lead_done: int = project_gap["lead_projects"]
        lead_req: int = project_gap["required_lead_projects"]

        total_score_max = PROJECT_MAX_SCORE * _TOTAL_WEIGHT
        lead_score_max = PROJECT_MAX_SCORE * _LEAD_WEIGHT

        if total_req == 0:
            total_score = total_score_max
        else:
            total_score = min(total_done / total_req, 1.0) * total_score_max

        if lead_req == 0:
            lead_score = lead_score_max
        else:
            lead_score = min(lead_done / lead_req, 1.0) * lead_score_max

        score = round(total_score + lead_score, 2)

        logger.info(
            "Project score for employee %s: %.2f / %.2f "
            "(projects=%d/%d, lead=%d/%d)",
            employee.employee_id,
            score,
            PROJECT_MAX_SCORE,
            total_done,
            total_req,
            lead_done,
            lead_req,
        )

        return ProjectScoreResult(
            completed=total_done,
            required=total_req,
            remaining=project_gap["remaining_projects"],
            lead_completed=lead_done,
            lead_required=lead_req,
            lead_remaining=project_gap["remaining_lead_projects"],
            score=score,
        )
