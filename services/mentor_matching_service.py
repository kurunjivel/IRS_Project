"""
Automated Peer & Mentor Matching Network — Phase 8.

Matches employees to relevant mentors and peers based on:
1. Target grade & role alignment.
2. Skill-gap coverage using Phase 7 exact + semantic matching.
3. Project & domain experience.
4. Relevant certifications.
5. Performance, experience, and availability.

Stateless service layer designed for high performance and fallback compatibility.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.employee import Employee
from database.employee_repository import EmployeeRepository
from database.recommendation_repository import RecommendationRepository
from services.semantic.semantic_matcher import SemanticMatcher
from services.gap_analysis_service import GapAnalysisService

logger = logging.getLogger(__name__)


@dataclass
class CoveredSkillGap:
    """Details of an employee skill gap covered by a candidate mentor."""
    required_skill: str
    mentor_skill: str
    match_type: str  # EXACT_MATCH, STRONG_SEMANTIC_MATCH, RELATED_SKILL, PARTIAL_RELEVANCE
    similarity_score: float
    mentor_proficiency: int
    required_level: int


@dataclass
class MentorMatchResult:
    """Detailed matching evaluation result for a candidate mentor or peer."""
    mentor_id: int
    full_name: str
    email: str
    department: str
    current_grade: str
    current_grade_id: int
    match_score: float  # 0.0 to 100.0
    match_level: str   # EXCELLENT, STRONG, GOOD, MODERATE
    match_type: str    # MENTOR, PEER_LEARNING_PARTNER
    performance_rating: float
    experience_years: float
    availability: bool
    skill_coverage_score: float
    grade_role_score: float
    project_score: float
    certification_score: float
    performance_score: float
    covered_gaps: List[CoveredSkillGap] = field(default_factory=list)
    match_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary representation."""
        return {
            "mentor_id": self.mentor_id,
            "full_name": self.full_name,
            "email": self.email,
            "department": self.department,
            "current_grade": self.current_grade,
            "current_grade_id": self.current_grade_id,
            "match_score": self.match_score,
            "match_level": self.match_level,
            "match_type": self.match_type,
            "performance_rating": self.performance_rating,
            "experience_years": self.experience_years,
            "availability": self.availability,
            "score_breakdown": {
                "skill_coverage": self.skill_coverage_score,
                "grade_role": self.grade_role_score,
                "project_experience": self.project_score,
                "certifications": self.certification_score,
                "performance_track": self.performance_score,
            },
            "covered_gaps": [
                {
                    "required_skill": cg.required_skill,
                    "mentor_skill": cg.mentor_skill,
                    "match_type": cg.match_type,
                    "similarity_score": cg.similarity_score,
                    "mentor_proficiency": cg.mentor_proficiency,
                    "required_level": cg.required_level,
                }
                for cg in self.covered_gaps
            ],
            "match_reasons": self.match_reasons,
        }


class MentorMatchingService:
    """
    Automated Peer & Mentor Matching Engine.
    """

    def __init__(
        self,
        emp_repo: Optional[EmployeeRepository] = None,
        rec_repo: Optional[RecommendationRepository] = None,
    ) -> None:
        self.emp_repo = emp_repo or EmployeeRepository()
        self.rec_repo = rec_repo or RecommendationRepository()
        self.semantic_matcher = SemanticMatcher()
        self.gap_service = GapAnalysisService()

    def find_matches(
        self,
        employee: Employee,
        skill_gaps: Optional[List[Dict[str, Any]]] = None,
        limit: int = 5,
    ) -> List[MentorMatchResult]:
        """
        Find and rank the best mentors and peer learning partners for an employee.

        Args:
            employee:   The target Employee model instance.
            skill_gaps: Optional list of skill gap dicts from GapAnalysisService.
                        If None, runs GapAnalysisService automatically.
            limit:      Maximum number of matches to return.

        Returns:
            List of MentorMatchResult ordered by match_score descending.
        """
        # 1. Ensure skill gaps are available
        if skill_gaps is None:
            gap_analysis = self.gap_service.run(employee.employee_id)
            skill_gaps = gap_analysis.get("skill_gaps", [])

        # Filter out satisfied gaps (only evaluate skills where gap > 0)
        unmet_gaps = [g for g in skill_gaps if g.get("gap", 0) > 0]

        # 2. Fetch candidate employees from DB
        raw_candidates = self.emp_repo.get_all_employees()

        # Fetch mentors table data for availability & specialization if present
        mentor_db_map = {}
        try:
            db_mentors = self.rec_repo.get_mentors_for_grade(employee.target_grade_id)
            for m in db_mentors:
                mid = m.get("mentor_id") or m.get("employee_id")
                if mid:
                    mentor_db_map[mid] = m
        except Exception as e:
            logger.warning("Could not fetch db_mentors table: %s", e)

        evaluated_matches: List[MentorMatchResult] = []

        for cand in raw_candidates:
            cand_id = cand["employee_id"]

            # Exclude self
            if cand_id == employee.employee_id:
                continue

            cand_grade_id = cand["current_grade_id"]

            # Candidate eligibility: Must be at least current grade, preferably target grade or above
            # Mentors: cand_grade_id >= target_grade_id
            # Peers: cand_grade_id == current_grade_id
            if cand_grade_id < employee.current_grade_id:
                continue

            # Load candidate's full skills, projects, and certifications
            cand_skills = self.emp_repo.get_employee_skills(cand_id)
            cand_projects = self.emp_repo.get_employee_projects(cand_id)
            cand_certs = self.emp_repo.get_employee_certifications(cand_id)

            # Check availability from mentors table or default to True
            m_info = mentor_db_map.get(cand_id, {})
            is_available = bool(m_info.get("availability", 1))

            # ---------------------------------------------------------
            # EVALUATION METRICS
            # ---------------------------------------------------------

            # 1. Skill-Gap Coverage (Weight: 35%)
            covered_gaps, skill_cov_score = self._evaluate_skill_gap_coverage(
                unmet_gaps, cand_skills
            )

            # 2. Grade & Target Role Alignment (Weight: 25%)
            grade_role_score, is_senior = self._evaluate_grade_role_alignment(
                employee, cand
            )

            # 3. Project & Domain Experience (Weight: 15%)
            project_score = self._evaluate_project_experience(
                employee, cand_projects
            )

            # 4. Certification Alignment (Weight: 10%)
            cert_score = self._evaluate_certifications(
                unmet_gaps, cand_certs
            )

            # 5. Performance & Track Record (Weight: 15%)
            perf_score = self._evaluate_performance(cand)

            # Total Weighted Composite Score (0.0 to 100.0)
            total_score = round(
                (skill_cov_score * 0.35)
                + (grade_role_score * 0.25)
                + (project_score * 0.15)
                + (cert_score * 0.10)
                + (perf_score * 0.15),
                1,
            )

            # Match Classification
            match_type = "MENTOR" if is_senior else "PEER_LEARNING_PARTNER"
            match_level = (
                "EXCELLENT" if total_score >= 80
                else "STRONG" if total_score >= 65
                else "GOOD" if total_score >= 50
                else "MODERATE"
            )

            # Generate Human-Readable Reasons
            reasons = self._build_match_reasons(
                cand, is_senior, covered_gaps, grade_role_score, project_score
            )

            result = MentorMatchResult(
                mentor_id=cand_id,
                full_name=cand["full_name"],
                email=cand["email"],
                department=cand["department"],
                current_grade=cand["current_grade"],
                current_grade_id=cand["current_grade_id"],
                match_score=total_score,
                match_level=match_level,
                match_type=match_type,
                performance_rating=float(cand.get("performance_rating", 3.0)),
                experience_years=float(cand.get("experience_years", 0.0)),
                availability=is_available,
                skill_coverage_score=round(skill_cov_score, 1),
                grade_role_score=round(grade_role_score, 1),
                project_score=round(project_score, 1),
                certification_score=round(cert_score, 1),
                performance_score=round(perf_score, 1),
                covered_gaps=covered_gaps,
                match_reasons=reasons,
            )

            evaluated_matches.append(result)

        # Sort matches by total match_score descending
        evaluated_matches.sort(key=lambda m: m.match_score, reverse=True)

        logger.info(
            "MentorMatchingService: Evaluated %d candidates for employee_id=%d. Returning top %d.",
            len(evaluated_matches), employee.employee_id, limit
        )
        return evaluated_matches[:limit]

    # ------------------------------------------------------------------
    # PRIVATE SCORING HELPERS
    # ------------------------------------------------------------------

    def _evaluate_skill_gap_coverage(
        self,
        unmet_gaps: List[Dict[str, Any]],
        cand_skills: List[Dict[str, Any]],
    ) -> tuple[List[CoveredSkillGap], float]:
        """
        Evaluate how well candidate's skills cover the employee's skill gaps using Phase 7 semantic matcher.
        """
        if not unmet_gaps:
            return [], 100.0

        if not cand_skills:
            return [], 0.0

        # Transform cand_skills into format expected by SemanticMatcher
        cand_skill_dicts = [
            {
                "skill_name": s.get("skill_name", ""),
                "skill_level": int(s.get("skill_level", 0)),
                "effective_level": float(s.get("skill_level", 0)),
                "category": s.get("category", ""),
            }
            for s in cand_skills
        ]

        covered_gaps: List[CoveredSkillGap] = []
        total_points = 0.0

        for gap in unmet_gaps:
            req_skill = gap.get("skill", "")
            req_level = int(gap.get("required_level", 1))

            # Match required skill against candidate's skills using Phase 7 SemanticMatcher
            match_res = self.semantic_matcher.match_skill(
                req_skill, float(req_level), cand_skill_dicts
            )

            if match_res.matched_employee_skill and match_res.match_type != "INSUFFICIENT_MATCH":
                cand_prof = int(match_res.employee_proficiency)
                # Check if candidate has sufficient level (>= 3 or >= req_level)
                if cand_prof >= min(req_level, 3):
                    # Points depend on match quality
                    mult = (
                        1.0 if match_res.match_type == "EXACT_MATCH"
                        else 0.85 if match_res.match_type == "STRONG_SEMANTIC_MATCH"
                        else 0.70 if match_res.match_type == "RELATED_SKILL"
                        else 0.50
                    )
                    total_points += (100.0 / len(unmet_gaps)) * mult

                    covered_gaps.append(
                        CoveredSkillGap(
                            required_skill=req_skill,
                            mentor_skill=match_res.matched_employee_skill,
                            match_type=match_res.match_type,
                            similarity_score=match_res.similarity_score,
                            mentor_proficiency=cand_prof,
                            required_level=req_level,
                        )
                    )

        coverage_percentage = min(100.0, total_points)
        return covered_gaps, coverage_percentage

    @staticmethod
    def _evaluate_grade_role_alignment(
        employee: Employee,
        cand: Dict[str, Any],
    ) -> tuple[float, bool]:
        """
        Evaluate grade senior status and target role similarity.
        """
        cand_grade_id = cand["current_grade_id"]
        target_grade_id = employee.target_grade_id
        current_grade_id = employee.current_grade_id

        is_senior = cand_grade_id >= target_grade_id
        score = 0.0

        if cand_grade_id > target_grade_id:
            score += 60.0  # Above target grade (e.g. G4 mentoring G2->G3)
        elif cand_grade_id == target_grade_id:
            score += 50.0  # Currently in target grade (e.g. G3 mentoring G2->G3)
        elif cand_grade_id == current_grade_id:
            score += 30.0  # Peer learning partner (same grade)

        # Department alignment bonus
        if cand.get("department", "").lower() == employee.department.lower():
            score += 40.0
        else:
            score += 20.0  # Cross-department insight

        return min(100.0, score), is_senior

    @staticmethod
    def _evaluate_project_experience(
        employee: Employee,
        cand_projects: List[Dict[str, Any]],
    ) -> float:
        """
        Evaluate candidate's project leadership and domain experience.
        """
        if not cand_projects:
            return 30.0

        score = 40.0
        has_lead = any(p.get("lead_project") for p in cand_projects)
        if has_lead:
            score += 30.0

        total_months = sum(p.get("duration_months", 0) for p in cand_projects)
        if total_months >= 24:
            score += 30.0
        elif total_months >= 12:
            score += 15.0

        return min(100.0, score)

    @staticmethod
    def _evaluate_certifications(
        unmet_gaps: List[Dict[str, Any]],
        cand_certs: List[Dict[str, Any]],
    ) -> float:
        """
        Evaluate candidate's certifications.
        """
        if not cand_certs:
            return 40.0

        completed = [c for c in cand_certs if c.get("status") == "Completed" or c.get("is_completed")]
        score = 50.0 + (len(completed) * 25.0)
        return min(100.0, score)

    @staticmethod
    def _evaluate_performance(cand: Dict[str, Any]) -> float:
        """
        Evaluate mentor performance rating and total experience.
        """
        rating = float(cand.get("performance_rating", 3.0))
        exp = float(cand.get("experience_years", 0.0))

        # Rating score (out of 70)
        rating_score = (rating / 5.0) * 70.0

        # Experience score (out of 30)
        exp_score = min(30.0, exp * 5.0)

        return min(100.0, rating_score + exp_score)

    @staticmethod
    def _build_match_reasons(
        cand: Dict[str, Any],
        is_senior: bool,
        covered_gaps: List[CoveredSkillGap],
        grade_role_score: float,
        project_score: float,
    ) -> List[str]:
        """
        Build clear, human-readable reasons explaining why this mentor/peer was recommended.
        """
        reasons: List[str] = []

        if is_senior:
            reasons.append(
                f"Currently holds {cand['current_grade']} (meets/exceeds your target grade)."
            )
        else:
            reasons.append(
                f"Holds {cand['current_grade']} as a peer learning partner pursuing a similar career path."
            )

        if covered_gaps:
            exact_count = sum(1 for cg in covered_gaps if cg.match_type == "EXACT_MATCH")
            semantic_count = len(covered_gaps) - exact_count

            gap_names = ", ".join([f"'{cg.required_skill}'" for cg in covered_gaps[:3]])
            if exact_count > 0 and semantic_count > 0:
                reasons.append(
                    f"Can help bridge {len(covered_gaps)} of your skill gaps ({gap_names}) via exact and semantic skill mastery."
                )
            elif exact_count > 0:
                reasons.append(
                    f"Possesses expert proficiency in your gap skills: {gap_names}."
                )
            else:
                reasons.append(
                    f"Has closely related semantic expertise in: {gap_names}."
                )

        if float(cand.get("performance_rating", 0.0)) >= 4.0:
            reasons.append(
                f"Consistently high performer (Rating: {cand['performance_rating']}/5.0)."
            )

        return reasons
