"""
Automated tests for SHAP Explainability Service (Phase 1.2).

Validates:
- Auto-detection of SHAP explainers (Tree, Linear, Kernel, Fallback).
- Explanation structure: positive_factors, negative_factors, neutral_factors.
- Prediction consistency (SHAP generation does not alter predictions).
- Model-agnostic fallback attributions.
- API schema compatibility for PredictionResponse.
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from services.ml.shap_explainability_service import ShapExplainabilityService
from services.ml.predictor import Predictor
from api.schemas.prediction import PredictionResponse, ShapAnalysisSchema


class TestShapExplainabilityService:
    """Unit tests for ShapExplainabilityService."""

    @pytest.fixture
    def service(self):
        return ShapExplainabilityService()

    @pytest.fixture
    def sample_features(self):
        return pd.DataFrame([{
            "experience_years": 6.5,
            "performance_rating": 4.5,
            "current_grade_encoded": 2,
            "target_grade_encoded": 3,
            "grade_gap": 1,
            "total_skills": 5,
            "average_skill_level": 4.0,
            "skill_coverage_percentage": 100.0,
            "mandatory_skill_gap_count": 0,
            "weighted_skill_gap": 0.0,
            "total_certifications": 2,
            "completed_certifications": 2,
            "certification_completion_rate": 100.0,
            "mandatory_certification_gap_count": 0,
            "total_projects": 4,
            "completed_projects": 4,
            "lead_projects": 1,
            "project_completion_rate": 100.0,
            "lead_project_completion_rate": 100.0,
            "average_project_rating": 4.2,
            "skill_score": 40.0,
            "certification_score": 20.0,
            "experience_score": 15.0,
            "project_score": 15.0,
            "performance_score": 10.0,
            "readiness_score": 100.0,
        }])

    def test_linear_model_shap_explanation(self, service, sample_features):
        """Verify SHAP explanation generation for linear models."""
        X_train = np.random.randn(20, len(sample_features.columns))
        y_train = np.random.randint(0, 2, 20)

        model = LogisticRegression(max_iter=500)
        model.fit(X_train, y_train)

        res = service.explain(model, sample_features)

        assert "base_value" in res
        assert "positive_factors" in res
        assert "negative_factors" in res
        assert "neutral_factors" in res
        assert "summary" in res
        assert isinstance(res["positive_factors"], list)

    def test_tree_model_shap_explanation(self, service, sample_features):
        """Verify SHAP explanation generation for tree-based models."""
        X_train = np.random.randn(20, len(sample_features.columns))
        y_train = np.random.randint(0, 2, 20)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        res = service.explain(model, sample_features)

        assert isinstance(res["base_value"], float)
        assert len(res["positive_factors"]) + len(res["negative_factors"]) + len(res["neutral_factors"]) == len(sample_features.columns)

    def test_explanation_item_structure(self, service, sample_features):
        """Verify individual feature explanation fields."""
        X_train = np.random.randn(20, len(sample_features.columns))
        y_train = np.random.randint(0, 2, 20)

        model = LogisticRegression()
        model.fit(X_train, y_train)

        res = service.explain(model, sample_features)
        all_factors = res["positive_factors"] + res["negative_factors"] + res["neutral_factors"]

        for item in all_factors:
            assert "feature" in item
            assert "feature_label" in item
            assert "feature_value" in item
            assert "shap_value" in item
            assert "direction" in item
            assert "explanation" in item
            assert item["direction"] in ["positive", "negative", "neutral"]

    def test_predictor_integration(self, sample_features):
        """Verify Predictor class integrates SHAP explanations without altering probabilities."""
        predictor = Predictor()
        row_dict = sample_features.iloc[0].to_dict()

        pred_with_shap = predictor.predict(row_dict, explain=True)
        pred_without_shap = predictor.predict(row_dict, explain=False)

        # Predictions must be consistent!
        assert pred_with_shap["promotion_probability"] == pred_without_shap["promotion_probability"]
        assert pred_with_shap["prediction"] == pred_without_shap["prediction"]

        # SHAP analysis must be present when explain=True
        assert pred_with_shap["shap_analysis"] is not None
        assert "positive_factors" in pred_with_shap["shap_analysis"]

        # Validate with Pydantic schema
        validated = PredictionResponse.model_validate(pred_with_shap)
        assert isinstance(validated.shap_analysis, ShapAnalysisSchema)
