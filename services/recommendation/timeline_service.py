"""
Timeline Service — IRS Phase 6.

Generates a personalised career progression timeline for an employee
based on their current gaps, readiness score, and ML prediction.

The timeline is advisory — it gives the employee a realistic estimate
of how long each area of improvement will take and when they can
realistically be promotion-ready.

Timeline logic
--------------
1. Skill development milestones   — based on gap severity and mandatory flag
2. Certification milestones       — based on missing certifications
3. Project milestones             — based on remaining project count
4. Experience milestone           — based on remaining experience years
5. Readiness milestone            — composite: "all gaps closed" target month
6. Promotion readiness milestone  — accounts for ML probability signal
"""

from __future__ import annotations

import logging
import math

from models.employee import Employee
from models.grade_requirement import GradeRequirement
from services.recommendation.recommendation_item import TimelineMilestone

logger = logging.getLogger(__name__)

# Months per course (rough estimate)
_MONTHS_PER_COURSE:        float = 1.5
# Months per certification (preparation + exam)
_MONTHS_PER_CERT:          float = 2.5
# Months per project
_MONTHS_PER_PROJECT:       float = 4.0
_MONTHS_PER_LEAD_PROJECT:  float = 6.0


class TimelineService:
    """
    Generates a career progression timeline from gap and ML data.

    Stateless — no mutable instance state.
    """

    def build(
        self,
        employee: Employee,
        requirement: GradeRequirement,
        gap_analysis: dict,
        readiness_score: float,
        promotion_probability: float,
    ) -> list[TimelineMilestone]:
        """
        Build the career progression timeline.

        Args:
            employee:              The loaded Employee object.
            requirement:           The GradeRequirement for the target grade.
            gap_analysis:          The dict returned by GapAnalysisService.run().
            readiness_score:       Phase 3 overall readiness score (0–100).
            promotion_probability: Phase 5 ML promotion probability (0–1).

        Returns:
            List of TimelineMilestone objects, ordered by month.
        """
        milestones: list[TimelineMilestone] = []
        current_month = 0

        skill_gaps     = gap_analysis.get("skill_gaps", [])
        cert_gaps      = gap_analysis.get("certification_gaps", [])
        project_gap    = gap_analysis.get("project_gap", {})
        experience_gap = gap_analysis.get("experience_gap", {})

        # ── 1. Skill milestones ───────────────────────────────────────────
        mandatory_gaps = [g for g in skill_gaps if g.get("mandatory")]
        optional_gaps  = [g for g in skill_gaps if not g.get("mandatory")]

        if mandatory_gaps:
            months = math.ceil(len(mandatory_gaps) * _MONTHS_PER_COURSE)
            current_month += months
            milestones.append(TimelineMilestone(
                month=current_month,
                title="Close mandatory skill gaps",
                description=(
                    f"Complete training for {len(mandatory_gaps)} mandatory skill(s): "
                    + ", ".join(g["skill"] for g in mandatory_gaps[:5])
                    + ("…" if len(mandatory_gaps) > 5 else "")
                ),
                category="Learning",
            ))

        if optional_gaps:
            months = math.ceil(len(optional_gaps) * _MONTHS_PER_COURSE)
            current_month += months
            milestones.append(TimelineMilestone(
                month=current_month,
                title="Develop recommended skills",
                description=(
                    f"Build proficiency in {len(optional_gaps)} optional skill(s): "
                    + ", ".join(g["skill"] for g in optional_gaps[:5])
                    + ("…" if len(optional_gaps) > 5 else "")
                ),
                category="Learning",
            ))

        # ── 2. Certification milestones ───────────────────────────────────
        mandatory_certs = [c for c in cert_gaps if c.get("mandatory")]
        optional_certs  = [c for c in cert_gaps if not c.get("mandatory")]

        if mandatory_certs:
            months = math.ceil(len(mandatory_certs) * _MONTHS_PER_CERT)
            current_month += months
            milestones.append(TimelineMilestone(
                month=current_month,
                title="Complete mandatory certifications",
                description=(
                    f"Obtain {len(mandatory_certs)} mandatory certification(s): "
                    + ", ".join(c["certification"] for c in mandatory_certs[:3])
                    + ("…" if len(mandatory_certs) > 3 else "")
                ),
                category="Certification",
            ))

        if optional_certs:
            months = math.ceil(len(optional_certs) * _MONTHS_PER_CERT)
            current_month += months
            milestones.append(TimelineMilestone(
                month=current_month,
                title="Pursue recommended certifications",
                description=(
                    f"Prepare for {len(optional_certs)} recommended certification(s): "
                    + ", ".join(c["certification"] for c in optional_certs[:3])
                ),
                category="Certification",
            ))

        # ── 3. Project milestones ─────────────────────────────────────────
        remaining_lead  = project_gap.get("remaining_lead_projects", 0)
        remaining_total = project_gap.get("remaining_projects", 0)

        if remaining_lead > 0:
            months = math.ceil(remaining_lead * _MONTHS_PER_LEAD_PROJECT)
            current_month += months
            milestones.append(TimelineMilestone(
                month=current_month,
                title=f"Complete {remaining_lead} lead project(s)",
                description=(
                    f"You need {remaining_lead} more lead project experience(s). "
                    "Seek leadership opportunities in your current or upcoming projects."
                ),
                category="Project",
            ))

        if remaining_total > 0:
            months = math.ceil(remaining_total * _MONTHS_PER_PROJECT)
            current_month += months
            milestones.append(TimelineMilestone(
                month=current_month,
                title=f"Complete {remaining_total} more project(s)",
                description=(
                    f"You need to participate in {remaining_total} more project(s) "
                    "to meet the grade requirement."
                ),
                category="Project",
            ))

        # ── 4. Experience milestone ───────────────────────────────────────
        remaining_exp_years = experience_gap.get("remaining_years", 0.0)
        if remaining_exp_years > 0:
            remaining_months = math.ceil(remaining_exp_years * 12)
            # Experience runs in parallel with other activities, so we
            # take the max of current_month and remaining_months
            current_month = max(current_month, remaining_months)
            milestones.append(TimelineMilestone(
                month=current_month,
                title=f"Gain {remaining_exp_years:.1f} more year(s) of experience",
                description=(
                    f"You currently have {experience_gap.get('current_years', 0):.1f} "
                    f"years of experience; "
                    f"{experience_gap.get('required_years', 0):.1f} years are required. "
                    "This is primarily time-based and runs in parallel with other activities."
                ),
                category="Experience",
            ))

        # ── 5. Readiness target milestone ─────────────────────────────────
        # If no gaps exist, the employee may already be near-ready
        if current_month == 0:
            current_month = 1

        # ML adjustment: low probability → add a buffer
        if promotion_probability < 0.50:
            buffer_months = math.ceil((0.50 - promotion_probability) * 12)
            current_month += buffer_months

        milestones.append(TimelineMilestone(
            month=current_month,
            title="Target: Promotion Ready",
            description=(
                f"Estimated readiness: {readiness_score:.0f}/100 now → 90+ after completing "
                "all recommended activities. "
                f"Current ML promotion probability: {promotion_probability:.0%}."
            ),
            category="Readiness",
        ))

        # ── Sort by month ─────────────────────────────────────────────────
        milestones.sort(key=lambda m: m.month)

        # Remove duplicate months by keeping the last milestone at each month
        deduped: list[TimelineMilestone] = []
        seen_months: set[int] = set()
        for m in reversed(milestones):
            if m.month not in seen_months:
                deduped.append(m)
                seen_months.add(m.month)
        milestones = list(reversed(deduped))
        milestones.sort(key=lambda m: m.month)

        logger.info(
            "TimelineService: %d milestone(s) generated for employee %s "
            "(estimated readiness month=%d).",
            len(milestones), employee.employee_id, current_month,
        )
        return milestones
