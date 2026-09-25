"""
Semantic Matcher — Phase 7.

Orchestrates exact and semantic skill matching using SkillNormalizationService,
EmbeddingService, and VectorStoreService with threshold classification and conservative gap calculations.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import numpy as np

from config import SEMANTIC_MATCHING_CONFIG
from services.semantic.skill_normalization_service import SkillNormalizationService
from services.semantic.embedding_service import EmbeddingService
from services.semantic.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


@dataclass
class SkillMatchResult:
    """Result of matching a required skill against an employee's skill set."""

    required_skill: str
    matched_employee_skill: Optional[str]
    match_type: str  # EXACT_MATCH, STRONG_SEMANTIC_MATCH, RELATED_SKILL, PARTIAL_RELEVANCE, INSUFFICIENT_MATCH
    similarity_score: float
    employee_proficiency: float
    required_proficiency: float
    effective_matched_level: float
    effective_match: bool
    gap_severity: str  # NONE, PARTIAL, FULL


_SIMILARITY_CACHE: dict[tuple[str, str], float] = {}


class SemanticMatcher:
    """Orchestrator for Exact + Semantic Skill Matching."""

    def __init__(self) -> None:
        self.normalizer = SkillNormalizationService()
        self.embedding_svc = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.thresholds = SEMANTIC_MATCHING_CONFIG.get("thresholds", {
            "STRONG_SEMANTIC_MATCH": 0.85,
            "RELATED_SKILL": 0.70,
            "PARTIAL_RELEVANCE": 0.55,
            "INSUFFICIENT_MATCH": 0.0,
        })

    def classify_similarity(self, similarity: float) -> str:
        """Classify similarity score into human-readable match type."""
        if similarity >= self.thresholds.get("STRONG_SEMANTIC_MATCH", 0.85):
            return "STRONG_SEMANTIC_MATCH"
        elif similarity >= self.thresholds.get("RELATED_SKILL", 0.70):
            return "RELATED_SKILL"
        elif similarity >= self.thresholds.get("PARTIAL_RELEVANCE", 0.55):
            return "PARTIAL_RELEVANCE"
        return "INSUFFICIENT_MATCH"

    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vector lists."""
        try:
            v1 = np.array(vec1, dtype=np.float32)
            v2 = np.array(vec2, dtype=np.float32)
            dot = float(np.dot(v1, v2))
            norm1 = float(np.linalg.norm(v1))
            norm2 = float(np.linalg.norm(v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)
        except Exception as e:
            logger.error("Error calculating cosine similarity: %s", e)
            return 0.0

    def match_skill(
        self,
        required_skill: str,
        required_level: float,
        employee_skills: List[Dict[str, Any]],
    ) -> SkillMatchResult:
        """
        Match a required skill against a list of employee skill dicts.

        employee_skills: List of dicts with keys: 'skill_name', 'skill_level', 'effective_level'
        """
        canonical_req = self.normalizer.normalize(required_skill)

        # Build map of employee skills
        emp_map = {}
        for s in employee_skills:
            orig_name = s.get("skill_name", "")
            canon_name = self.normalizer.normalize(orig_name)
            emp_map[canon_name.lower()] = s

        # ----------------------------------------------------
        # STEP 1: Exact Match Check First
        # ----------------------------------------------------
        req_key = canonical_req.lower()
        if req_key in emp_map:
            emp_s = emp_map[req_key]
            emp_level = float(emp_s.get("effective_level", emp_s.get("skill_level", 0)))
            is_full = emp_level >= required_level
            gap_sev = "NONE" if is_full else "PARTIAL"

            return SkillMatchResult(
                required_skill=required_skill,
                matched_employee_skill=emp_s.get("skill_name", required_skill),
                match_type="EXACT_MATCH",
                similarity_score=1.0,
                employee_proficiency=emp_level,
                required_proficiency=required_level,
                effective_matched_level=emp_level,
                effective_match=is_full,
                gap_severity=gap_sev,
            )

        # ----------------------------------------------------
        # STEP 2: Semantic Vector Similarity Fallback
        # ----------------------------------------------------
        best_match_skill = None
        best_similarity = 0.0
        best_emp_level = 0.0

        if self.embedding_svc.is_available and employee_skills:
            req_text = self.normalizer.get_embedding_text(canonical_req)
            req_vec = self.embedding_svc.generate_embedding(req_text)
            if req_vec:
                for s in employee_skills:
                    s_name = s.get("skill_name", "")
                    if self.normalizer.is_distinct_language_pair(canonical_req, s_name):
                        continue
                    s_text = self.normalizer.get_embedding_text(s_name, s.get("category"))
                    
                    cache_key = (req_text.lower(), s_text.lower())
                    if cache_key in _SIMILARITY_CACHE:
                        sim = _SIMILARITY_CACHE[cache_key]
                    else:
                        s_vec = self.embedding_svc.generate_embedding(s_text)
                        if s_vec:
                            sim = self.calculate_cosine_similarity(req_vec, s_vec)
                            _SIMILARITY_CACHE[cache_key] = sim
                        else:
                            sim = 0.0

                    if sim > best_similarity:
                        best_similarity = sim
                        best_match_skill = s_name
                        best_emp_level = float(s.get("effective_level", s.get("skill_level", 0)))

        match_type = self.classify_similarity(best_similarity)

        # ----------------------------------------------------
        # STEP 3: Conservative Gap Calculation
        # ----------------------------------------------------
        if match_type in ("STRONG_SEMANTIC_MATCH", "RELATED_SKILL", "PARTIAL_RELEVANCE"):
            # Partial level credit = similarity_score * employee_level
            effective_matched_level = round(best_similarity * best_emp_level, 2)
            is_full = (effective_matched_level >= required_level) and (match_type == "STRONG_SEMANTIC_MATCH")
            gap_sev = "PARTIAL" if effective_matched_level > 0 else "FULL"

            return SkillMatchResult(
                required_skill=required_skill,
                matched_employee_skill=best_match_skill,
                match_type=match_type,
                similarity_score=round(best_similarity, 4),
                employee_proficiency=best_emp_level,
                required_proficiency=required_level,
                effective_matched_level=effective_matched_level,
                effective_match=is_full,
                gap_severity=gap_sev,
            )

        # No match or insufficient match fallback
        return SkillMatchResult(
            required_skill=required_skill,
            matched_employee_skill=None,
            match_type="INSUFFICIENT_MATCH",
            similarity_score=round(best_similarity, 4),
            employee_proficiency=0.0,
            required_proficiency=required_level,
            effective_matched_level=0.0,
            effective_match=False,
            gap_severity="FULL",
        )
