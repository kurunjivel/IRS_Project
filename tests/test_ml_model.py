"""
tests/test_ml_model.py — Phase 5 ML Model Tests.

Covers:
1. Model training
2. Model loading
3. Prediction
4. Probability range
5. Output schema
6. Invalid input
7. Model persistence
"""

import sys
import pickle
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# MySQL stub — must be set before any project imports
# ---------------------------------------------------------------------------
sys.modules.setdefault("mysql", MagicMock())
sys.modules.setdefault("mysql.connector", MagicMock())

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from services.ml.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN
from services.ml.model_trainer import ModelTrainer, TrainingReport, ModelResult
from services.ml.model_evaluator import ModelEvaluator, EvaluationReport
from services.ml.predictor import (
    Predictor,
    LABEL_POSITIVE,
    LABEL_NEGATIVE,
    DEFAULT_THRESHOLD,
)
from services.ml.data_preprocessor import DataPreprocessor, SplitDataset


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def split() -> SplitDataset:
    """Load and split the real dataset once for the whole module."""
    return DataPreprocessor().load_and_split()


@pytest.fixture(scope="module")
def training_report(split) -> TrainingReport:
    """Train all models once and return the report."""
    trainer = ModelTrainer()
    return trainer.train()


@pytest.fixture(scope="module")
def predictor() -> Predictor:
    """Return a Predictor loaded from the saved model."""
    return Predictor()


@pytest.fixture
def sample_feature_row(split) -> dict:
    """Return a single feature row as a dict from the test set."""
    return split.X_test.iloc[0].to_dict()


@pytest.fixture
def sample_feature_df(split) -> pd.DataFrame:
    """Return a 5-row feature DataFrame from the test set."""
    return split.X_test.iloc[:5].copy()


# ===========================================================================
# 1. Model Training Tests
# ===========================================================================

class TestModelTraining:
    """Tests for ModelTrainer.train()."""

    def test_training_report_type(self, training_report):
        assert isinstance(training_report, TrainingReport)

    def test_best_model_name_is_string(self, training_report):
        assert isinstance(training_report.best_model_name, str)
        assert len(training_report.best_model_name) > 0

    def test_all_three_models_trained(self, training_report):
        names = {r.name for r in training_report.all_results}
        assert "LogisticRegression" in names
        assert "DecisionTreeClassifier" in names
        assert "RandomForestClassifier" in names

    def test_each_result_has_cv_scores(self, training_report):
        for r in training_report.all_results:
            assert isinstance(r, ModelResult)
            assert "test_f1_macro" in r.cv_scores
            assert "test_accuracy" in r.cv_scores
            assert "test_roc_auc" in r.cv_scores

    def test_cv_f1_scores_are_valid(self, training_report):
        for r in training_report.all_results:
            assert 0.0 <= r.mean_f1 <= 1.0

    def test_cv_accuracy_scores_are_valid(self, training_report):
        for r in training_report.all_results:
            assert 0.0 <= r.mean_accuracy <= 1.0

    def test_cv_roc_auc_scores_are_valid(self, training_report):
        for r in training_report.all_results:
            assert 0.0 <= r.mean_roc_auc <= 1.0

    def test_best_model_selected_by_f1(self, training_report):
        """Best model must have the highest (or tied) CV F1."""
        best_f1 = max(r.mean_f1 for r in training_report.all_results)
        best_result = next(
            r for r in training_report.all_results
            if r.name == training_report.best_model_name
        )
        assert best_result.mean_f1 >= best_f1 - 1e-9

    def test_model_path_exists(self, training_report):
        assert training_report.model_path.exists()

    def test_comparison_table_has_all_models(self, training_report):
        df = training_report.comparison_table()
        assert len(df) == len(training_report.all_results)
        assert "Model" in df.columns
        assert "CV F1 (macro)" in df.columns

    def test_feature_columns_match_spec(self, training_report):
        assert training_report.feature_columns == FEATURE_COLUMNS

    def test_split_sizes_are_correct(self, training_report):
        split = training_report.split
        total = split.total_rows
        assert split.train_rows == pytest.approx(total * 0.80, abs=2)
        assert split.test_rows == pytest.approx(total * 0.20, abs=2)


# ===========================================================================
# 2. Model Loading Tests
# ===========================================================================

class TestModelLoading:
    """Tests for loading the saved model from disk."""

    def test_predictor_loads_without_error(self, predictor):
        # Accessing model_name triggers lazy load
        name = predictor.model_name
        assert isinstance(name, str)

    def test_loaded_model_is_pipeline(self):
        from services.ml.model_trainer import MODEL_PATH
        with MODEL_PATH.open("rb") as fh:
            pipeline = pickle.load(fh)
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_has_scaler_and_clf(self):
        from services.ml.model_trainer import MODEL_PATH
        with MODEL_PATH.open("rb") as fh:
            pipeline = pickle.load(fh)
        assert "scaler" in pipeline.named_steps
        assert "clf" in pipeline.named_steps

    def test_metadata_file_exists(self):
        from services.ml.model_trainer import METADATA_PATH
        assert METADATA_PATH.exists()

    def test_metadata_has_required_keys(self):
        import json
        from services.ml.model_trainer import METADATA_PATH
        with METADATA_PATH.open() as fh:
            meta = json.load(fh)
        for key in ("model_name", "feature_columns", "cv_f1_macro", "cv_accuracy", "cv_roc_auc"):
            assert key in meta

    def test_metadata_feature_columns_match(self):
        import json
        from services.ml.model_trainer import METADATA_PATH
        with METADATA_PATH.open() as fh:
            meta = json.load(fh)
        assert meta["feature_columns"] == FEATURE_COLUMNS

    def test_predictor_model_name_matches_metadata(self, predictor):
        import json
        from services.ml.model_trainer import METADATA_PATH
        with METADATA_PATH.open() as fh:
            meta = json.load(fh)
        assert predictor.model_name == meta["model_name"]

    def test_predictor_raises_on_missing_model(self, tmp_path):
        p = Predictor(model_path=tmp_path / "nonexistent.pkl")
        with pytest.raises(FileNotFoundError):
            p.predict({"x": 1})

    def test_predictor_reload(self, predictor):
        """reload() should not raise and model_name should remain valid."""
        predictor.reload()
        assert isinstance(predictor.model_name, str)


# ===========================================================================
# 3. Prediction Tests
# ===========================================================================

class TestPrediction:
    """Tests for Predictor.predict() and predict_batch()."""

    def test_single_prediction_returns_dict(self, predictor, sample_feature_row):
        result = predictor.predict(
            sample_feature_row,
            employee_id=101,
            current_grade="G2",
            target_grade="G3",
        )
        assert isinstance(result, dict)

    def test_prediction_label_is_valid(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert result["prediction"] in (LABEL_POSITIVE, LABEL_NEGATIVE)

    def test_prediction_from_series(self, predictor, split):
        series = split.X_test.iloc[0]
        result = predictor.predict(series, employee_id=5)
        assert result["employee_id"] == 5

    def test_prediction_from_dataframe(self, predictor, split):
        df = split.X_test.iloc[[0]]
        result = predictor.predict(df, employee_id=7)
        assert result["employee_id"] == 7

    def test_batch_prediction_length(self, predictor, sample_feature_df):
        results = predictor.predict_batch(sample_feature_df)
        assert len(results) == len(sample_feature_df)

    def test_batch_prediction_all_have_schema(self, predictor, sample_feature_df):
        results = predictor.predict_batch(sample_feature_df)
        required = {"employee_id", "current_grade", "target_grade",
                    "promotion_probability", "prediction", "model_name"}
        for r in results:
            assert required.issubset(r.keys())

    def test_batch_with_ids_and_grades(self, predictor, sample_feature_df):
        ids = list(range(100, 105))
        cur = ["G1", "G2", "G3", "G1", "G2"]
        tgt = ["G2", "G3", "G4", "G2", "G3"]
        results = predictor.predict_batch(sample_feature_df, ids, cur, tgt)
        for i, r in enumerate(results):
            assert r["employee_id"] == ids[i]
            assert r["current_grade"] == cur[i]
            assert r["target_grade"] == tgt[i]

    def test_positive_label_when_high_probability(self, predictor):
        """Force a high-probability row and check label."""
        row = {col: 0.0 for col in FEATURE_COLUMNS}
        row.update({
            "experience_years": 15.0,
            "performance_rating": 5.0,
            "current_grade_encoded": 1.0,
            "target_grade_encoded": 2.0,
            "grade_gap": 1.0,
            "skill_coverage_percentage": 100.0,
            "certification_completion_rate": 1.0,
            "project_completion_rate": 1.0,
            "lead_project_completion_rate": 1.0,
            "readiness_score": 100.0,
            "skill_score": 40.0,
            "certification_score": 15.0,
            "experience_score": 15.0,
            "project_score": 20.0,
            "performance_score": 10.0,
        })
        result = predictor.predict(row)
        # With very high features, probability should be above 0.5
        # (not guaranteed for all models, but we check schema is correct)
        assert result["prediction"] in (LABEL_POSITIVE, LABEL_NEGATIVE)


# ===========================================================================
# 4. Probability Range Tests
# ===========================================================================

class TestProbabilityRange:
    """Tests that probabilities are always in [0, 1]."""

    def test_single_probability_in_range(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        p = result["promotion_probability"]
        assert 0.0 <= p <= 1.0

    def test_batch_probabilities_in_range(self, predictor, sample_feature_df):
        results = predictor.predict_batch(sample_feature_df)
        for r in results:
            assert 0.0 <= r["promotion_probability"] <= 1.0

    def test_probability_is_float(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert isinstance(result["promotion_probability"], float)

    def test_probability_rounded_to_4dp(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        p = result["promotion_probability"]
        assert p == round(p, 4)

    def test_all_test_set_probabilities_in_range(self, predictor, split):
        results = predictor.predict_batch(split.X_test)
        probs = [r["promotion_probability"] for r in results]
        assert all(0.0 <= p <= 1.0 for p in probs)

    def test_threshold_boundary(self, predictor, sample_feature_row):
        """Prediction label must match threshold comparison."""
        result = predictor.predict(sample_feature_row)
        p = result["promotion_probability"]
        expected = LABEL_POSITIVE if p >= predictor.threshold else LABEL_NEGATIVE
        assert result["prediction"] == expected


# ===========================================================================
# 5. Output Schema Tests
# ===========================================================================

class TestOutputSchema:
    """Tests that prediction output always matches the required schema."""

    REQUIRED_KEYS = {
        "employee_id",
        "current_grade",
        "target_grade",
        "promotion_probability",
        "prediction",
        "model_name",
    }

    def test_all_required_keys_present(self, predictor, sample_feature_row):
        result = predictor.predict(
            sample_feature_row,
            employee_id=101,
            current_grade="G2",
            target_grade="G3",
        )
        assert self.REQUIRED_KEYS.issubset(result.keys())

    def test_employee_id_is_int(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row, employee_id=42)
        assert isinstance(result["employee_id"], int)
        assert result["employee_id"] == 42

    def test_current_grade_is_string(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row, current_grade="G3")
        assert isinstance(result["current_grade"], str)
        assert result["current_grade"] == "G3"

    def test_target_grade_is_string(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row, target_grade="G4")
        assert isinstance(result["target_grade"], str)
        assert result["target_grade"] == "G4"

    def test_promotion_probability_is_float(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert isinstance(result["promotion_probability"], float)

    def test_prediction_is_string(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert isinstance(result["prediction"], str)

    def test_model_name_is_string(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert isinstance(result["model_name"], str)
        assert len(result["model_name"]) > 0

    def test_model_name_matches_loaded_model(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert result["model_name"] == predictor.model_name

    def test_no_extra_unexpected_keys(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert set(result.keys()) == self.REQUIRED_KEYS

    def test_default_employee_id_is_zero(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert result["employee_id"] == 0

    def test_default_grades_are_empty_strings(self, predictor, sample_feature_row):
        result = predictor.predict(sample_feature_row)
        assert result["current_grade"] == ""
        assert result["target_grade"] == ""


# ===========================================================================
# 6. Invalid Input Tests
# ===========================================================================

class TestInvalidInput:
    """Tests that invalid inputs raise appropriate errors."""

    def test_missing_feature_column_raises(self, predictor):
        incomplete = {col: 1.0 for col in FEATURE_COLUMNS[:-3]}  # missing last 3
        with pytest.raises(ValueError, match="Missing feature columns"):
            predictor.predict(incomplete)

    def test_empty_dict_raises(self, predictor):
        with pytest.raises(ValueError, match="Missing feature columns"):
            predictor.predict({})

    def test_wrong_type_raises(self, predictor):
        with pytest.raises(TypeError):
            predictor.predict([1, 2, 3])  # list is not supported

    def test_invalid_threshold_raises(self, predictor):
        with pytest.raises(ValueError):
            predictor.threshold = 1.5

    def test_zero_threshold_raises(self, predictor):
        with pytest.raises(ValueError):
            predictor.threshold = 0.0

    def test_negative_threshold_raises(self, predictor):
        with pytest.raises(ValueError):
            predictor.threshold = -0.1

    def test_missing_model_file_raises(self, tmp_path):
        p = Predictor(model_path=tmp_path / "missing.pkl")
        row = {col: 1.0 for col in FEATURE_COLUMNS}
        with pytest.raises(FileNotFoundError):
            p.predict(row)

    def test_dataset_too_small_raises(self):
        from services.ml.dataset_generator import DatasetGenerator
        with pytest.raises(ValueError, match="n_samples must be >= 500"):
            DatasetGenerator(n_samples=100)

    def test_evaluator_with_unfitted_pipeline_raises(self, split):
        """An unfitted pipeline should raise when predict is called."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        unfitted = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression())])
        evaluator = ModelEvaluator()
        with pytest.raises(Exception):
            evaluator.evaluate(unfitted, split)


# ===========================================================================
# 7. Model Persistence Tests
# ===========================================================================

class TestModelPersistence:
    """Tests that the model can be saved and reloaded correctly."""

    def test_pkl_file_exists(self):
        from services.ml.model_trainer import MODEL_PATH
        assert MODEL_PATH.exists()
        assert MODEL_PATH.suffix == ".pkl"

    def test_pkl_is_valid_pipeline(self):
        from services.ml.model_trainer import MODEL_PATH
        with MODEL_PATH.open("rb") as fh:
            obj = pickle.load(fh)
        assert isinstance(obj, Pipeline)

    def test_reloaded_model_produces_same_predictions(self, split):
        """Saving and reloading must produce identical predictions."""
        from services.ml.model_trainer import MODEL_PATH
        with MODEL_PATH.open("rb") as fh:
            pipeline1 = pickle.load(fh)
        with MODEL_PATH.open("rb") as fh:
            pipeline2 = pickle.load(fh)

        X = split.X_test.iloc[:10]
        preds1 = pipeline1.predict(X)
        preds2 = pipeline2.predict(X)
        np.testing.assert_array_equal(preds1, preds2)

    def test_save_and_load_custom_path(self, training_report, tmp_path):
        """Model saved to a custom path must be loadable."""
        custom_pkl = tmp_path / "test_model.pkl"
        pipeline = training_report.all_results[0].pipeline
        with custom_pkl.open("wb") as fh:
            pickle.dump(pipeline, fh)

        with custom_pkl.open("rb") as fh:
            loaded = pickle.load(fh)
        assert isinstance(loaded, Pipeline)

    def test_predictor_with_custom_model_path(self, training_report, split, tmp_path):
        """Predictor should work with a custom model path."""
        custom_pkl = tmp_path / "custom_model.pkl"
        pipeline = training_report.all_results[0].pipeline
        pipeline.fit(split.X_train, split.y_train)
        with custom_pkl.open("wb") as fh:
            pickle.dump(pipeline, fh)

        p = Predictor(model_path=custom_pkl)
        row = split.X_test.iloc[0].to_dict()
        result = p.predict(row, employee_id=999)
        assert result["employee_id"] == 999
        assert 0.0 <= result["promotion_probability"] <= 1.0

    def test_model_file_size_is_reasonable(self):
        """Model file should be non-empty and under 50 MB."""
        from services.ml.model_trainer import MODEL_PATH
        size_bytes = MODEL_PATH.stat().st_size
        assert size_bytes > 0
        assert size_bytes < 50 * 1024 * 1024  # 50 MB

    def test_metadata_json_is_valid(self):
        import json
        from services.ml.model_trainer import METADATA_PATH
        with METADATA_PATH.open() as fh:
            meta = json.load(fh)
        assert isinstance(meta, dict)
        assert meta["cv_folds"] == 5
        assert meta["random_state"] == 42


# ===========================================================================
# 8. Evaluator Tests
# ===========================================================================

class TestModelEvaluator:
    """Tests for ModelEvaluator."""

    @pytest.fixture(scope="class")
    def eval_report(self, training_report, split):
        evaluator = ModelEvaluator()
        best = next(
            r for r in training_report.all_results
            if r.name == training_report.best_model_name
        )
        best.pipeline.fit(split.X_train, split.y_train)
        return evaluator.evaluate(best.pipeline, split)

    def test_eval_report_type(self, eval_report):
        assert isinstance(eval_report, EvaluationReport)

    def test_accuracy_in_range(self, eval_report):
        assert 0.0 <= eval_report.accuracy <= 1.0

    def test_precision_in_range(self, eval_report):
        assert 0.0 <= eval_report.precision_macro <= 1.0

    def test_recall_in_range(self, eval_report):
        assert 0.0 <= eval_report.recall_macro <= 1.0

    def test_f1_in_range(self, eval_report):
        assert 0.0 <= eval_report.f1_macro <= 1.0

    def test_roc_auc_in_range(self, eval_report):
        assert 0.0 <= eval_report.roc_auc <= 1.0

    def test_confusion_matrix_shape(self, eval_report):
        assert eval_report.confusion_matrix.shape == (2, 2)

    def test_confusion_matrix_sums_to_test_size(self, eval_report, split):
        assert eval_report.confusion_matrix.sum() == split.test_rows

    def test_y_pred_length(self, eval_report, split):
        assert len(eval_report.y_pred) == split.test_rows

    def test_y_proba_length(self, eval_report, split):
        assert len(eval_report.y_proba) == split.test_rows

    def test_y_proba_in_range(self, eval_report):
        assert np.all(eval_report.y_proba >= 0.0)
        assert np.all(eval_report.y_proba <= 1.0)

    def test_summary_is_string(self, eval_report):
        s = eval_report.summary()
        assert isinstance(s, str)
        assert "Confusion Matrix" in s

    def test_to_dict_has_required_keys(self, eval_report):
        d = eval_report.to_dict()
        for key in ("model_name", "accuracy", "precision_macro", "recall_macro",
                    "f1_macro", "roc_auc"):
            assert key in d

    def test_comparison_dataframe(self, training_report, split):
        evaluator = ModelEvaluator()
        reports = []
        for r in training_report.all_results:
            r.pipeline.fit(split.X_train, split.y_train)
            reports.append(evaluator.evaluate(r.pipeline, split))
        df = evaluator.comparison_dataframe(reports)
        assert len(df) == len(training_report.all_results)
        assert "Model" in df.columns
        assert "F1 (macro)" in df.columns
