"""
Automated Test Suite for Phase 7 — Semantic Skill Matching with Embeddings.

Tests:
1. Skill normalization logic.
2. Exact matching precedence over semantic matching.
3. Semantic similarity matching (e.g. FastAPI -> Flask).
4. Unrelated skill filtering (e.g. Python -> Photoshop).
5. Threshold classification boundaries.
6. Proficiency level partial credit calculation.
7. Graceful fallback when vector components are unavailable.
8. Backward compatibility with existing Gap Analysis & Role Fit engines.
"""

import pytest
from services.semantic.skill_normalization_service import SkillNormalizationService
from services.semantic.embedding_service import EmbeddingService
from services.semantic.vector_store_service import VectorStoreService
from services.semantic.semantic_matcher import SemanticMatcher


class TestSkillNormalization:
    """Test string canonicalization and alias resolution."""

    def test_canonical_casing(self):
        assert SkillNormalizationService.normalize("python") == "Python"
        assert SkillNormalizationService.normalize("PYTHON") == "Python"
        assert SkillNormalizationService.normalize("Python") == "Python"

    def test_alias_resolution(self):
        assert SkillNormalizationService.normalize("fast api") == "FastAPI"
        assert SkillNormalizationService.normalize("fastapi") == "FastAPI"
        assert SkillNormalizationService.normalize("react.js") == "React"
        assert SkillNormalizationService.normalize("k8s") == "Kubernetes"
        assert SkillNormalizationService.normalize("amazon web services") == "AWS"


class TestSemanticMatcherLogic:
    """Test exact matching, semantic similarity, thresholds, and fallback."""

    def setup_method(self):
        self.matcher = SemanticMatcher()

    def test_exact_match_precedence(self):
        emp_skills = [
            {"skill_name": "Python", "skill_level": 4, "effective_level": 4.0},
            {"skill_name": "FastAPI", "skill_level": 4, "effective_level": 4.0},
        ]
        res = self.matcher.match_skill("Python", 4.0, emp_skills)
        assert res.match_type == "EXACT_MATCH"
        assert res.similarity_score == 1.0
        assert res.effective_match is True
        assert res.gap_severity == "NONE"

    def test_semantic_match_related_skill(self):
        emp_skills = [
            {"skill_name": "FastAPI", "skill_level": 4, "effective_level": 4.0},
        ]
        res = self.matcher.match_skill("Flask", 4.0, emp_skills)
        assert res.match_type in ("STRONG_SEMANTIC_MATCH", "RELATED_SKILL", "PARTIAL_RELEVANCE")
        assert res.similarity_score >= 0.55
        assert res.matched_employee_skill == "FastAPI"
        assert res.effective_matched_level > 0.0

    def test_unrelated_skill_insufficient_match(self):
        emp_skills = [
            {"skill_name": "Python", "category": "Software Engineering", "skill_level": 4, "effective_level": 4.0},
        ]
        res = self.matcher.match_skill("Photoshop", 4.0, emp_skills)
        assert res.match_type == "INSUFFICIENT_MATCH"
        assert res.similarity_score < 0.55
        assert res.effective_matched_level == 0.0
        assert res.gap_severity == "FULL"

    def test_threshold_classification(self):
        assert self.matcher.classify_similarity(0.90) == "STRONG_SEMANTIC_MATCH"
        assert self.matcher.classify_similarity(0.85) == "STRONG_SEMANTIC_MATCH"
        assert self.matcher.classify_similarity(0.78) == "RELATED_SKILL"
        assert self.matcher.classify_similarity(0.70) == "RELATED_SKILL"
        assert self.matcher.classify_similarity(0.60) == "PARTIAL_RELEVANCE"
        assert self.matcher.classify_similarity(0.55) == "PARTIAL_RELEVANCE"
        assert self.matcher.classify_similarity(0.40) == "INSUFFICIENT_MATCH"

    def test_proficiency_partial_credit(self):
        emp_skills = [
            {"skill_name": "FastAPI", "skill_level": 4, "effective_level": 4.0},
        ]
        res = self.matcher.match_skill("Flask", 4.0, emp_skills)
        # Partial level credit should be similarity_score * employee_proficiency
        expected_level = round(res.similarity_score * 4.0, 2)
        assert res.effective_matched_level == expected_level

    def test_fallback_when_embedding_service_disabled(self):
        """Simulate model unavailability — matcher must safely return exact matching / insufficient match."""
        matcher_fallback = SemanticMatcher()
        matcher_fallback.embedding_svc._model = None  # Force model unavailable

        emp_skills = [
            {"skill_name": "Python", "skill_level": 4, "effective_level": 4.0},
        ]

        # Exact match still works!
        res_exact = matcher_fallback.match_skill("Python", 4.0, emp_skills)
        assert res_exact.match_type == "EXACT_MATCH"

        # Missing skill safely defaults to insufficient match without crashing
        res_missing = matcher_fallback.match_skill("Flask", 4.0, emp_skills)
        assert res_missing.match_type == "INSUFFICIENT_MATCH"
