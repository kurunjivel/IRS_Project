"""
Unit tests for IRS Phase 4 — ML Dataset + Feature Engineering.

Test classes
------------
TestSyntheticDatasetGenerator   — shape, dtypes, ranges, reproducibility,
                                   class balance, disclaimer
TestFeatureEngineer             — live extraction from Phase 2/3 objects
TestDataFrameFeatureEngineer    — validation, clipping, get_X_y, error paths
TestDatasetBuilder              — build_and_save, load, load_raw, path handling
TestFeatureNames                — FEATURE_NAMES contract (order, count, no dups)

All tests are self-contained — no live database, no file-system side effects
(DatasetBuilder tests use a temporary directory).
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Stub mysql.connector before any project module is imported
# ---------------------------------------------------------------------------
_mysql_stub = MagicMock()
sys.modules.setdefault("mysql", _mysql_stub)
sys.modules.setdefault("mysql.connector", _mysql_stub)
sys.modules.setdefault("mysql.connector.pooling", _mysql_stub)

import numpy as np
import pandas as pd

from models.employee import Employee, EmployeeSkill, EmployeeCertification, EmployeeProject
from models.grade_requirement import (
    GradeRequirement,
    GradeSkillRequirement,
    GradeCertificationRequirement,
    GradeProjectRequirement,
)
from ml.synthetic_data_generator import (
    SyntheticDatasetGenerator,
    SyntheticDatasetConfig,
    SYNTHETIC_DATA_DISCLAIMER,
)
from ml.feature_engineering import (
    FeatureEngineer,
    DataFrameFeatureEngineer,
    FeatureVector,
    FEATURE_NAMES,
    TARGET_COLUMN,
)
from ml.dataset_builder import DatasetBuilder


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_employee(**overrides) -> Employee:
    defaults = dict(
        employee_id=1,
        employee_code="EMP001",
        full_name="Alice Smith",
        email="alice@example.com",
        department="Engineering",
        experience_years=5.0,
        performance_rating=4.0,
        joining_date="2019-01-01",
        current_grade="G2",
        current_grade_id=2,
        target_grade="G3",
        target_grade_id=3,
        skills=[
            EmployeeSkill("Python", "Backend", 4),
            EmployeeSkill("AWS", "Cloud", 3),
        ],
        certifications=[
            EmployeeCertification("AWS-CCP", "Amazon", "Completed", "2023-01-01", None),
        ],
        projects=[
            EmployeeProject("Alpha", "Python", "Hard", "Finance", "Lead", True, 6, 4.5),
            EmployeeProject("Beta", "AWS", "Medium", "HR", "Dev", False, 4, 3.8),
        ],
    )
    defaults.update(overrides)
    return Employee(**defaults)


def _make_requirement(**overrides) -> GradeRequirement:
    defaults = dict(
        grade_id=3,
        grade_name="G3",
        description="Mid-senior level",
        skills=[
            GradeSkillRequirement("Python", "Backend", 5, 1.0, True),
            GradeSkillRequirement("AWS", "Cloud", 4, 0.8, False),
        ],
        certifications=[
            GradeCertificationRequirement("AWS-CCP", "Amazon", True),
        ],
        project_requirement=GradeProjectRequirement(
            minimum_projects=3,
            minimum_lead_projects=1,
            minimum_experience=4.0,
        ),
    )
    defaults.update(overrides)
    return GradeRequirement(**defaults)


def _make_gap_analysis(employee: Employee, requirement: GradeRequirement) -> dict:
    """Build a gap_analysis dict using the real Phase 2 services."""
    from services.skill_gap_service import SkillGapService
    from services.certification_gap_service import CertificationGapService
    from services.experience_gap_service import ExperienceGapService
    from services.project_gap_service import ProjectGapService

    return {
        "employee": employee,
        "requirement": requirement,
        "skill_gaps": SkillGapService().analyze(employee, requirement),
        "certification_gaps": CertificationGapService().analyze(employee, requirement),
        "experience_gap": ExperienceGapService().analyze(employee, requirement),
        "project_gap": ProjectGapService().analyze(employee, requirement),
    }


def _make_readiness_result(gap_analysis: dict):
    """Build a ReadinessResult using the real Phase 3 engine."""
    from services.readiness.readiness_engine import ReadinessEngine
    return ReadinessEngine().calculate(gap_analysis)


# ---------------------------------------------------------------------------
# TestFeatureNames
# ---------------------------------------------------------------------------

class TestFeatureNames(unittest.TestCase):
    """Contract tests for the FEATURE_NAMES constant."""

    def test_count(self) -> None:
        """There must be exactly 18 features."""
        self.assertEqual(len(FEATURE_NAMES), 18)

    def test_no_duplicates(self) -> None:
        """Every feature name must be unique."""
        self.assertEqual(len(FEATURE_NAMES), len(set(FEATURE_NAMES)))

    def test_all_strings(self) -> None:
        """Every entry must be a non-empty string."""
        for name in FEATURE_NAMES:
            self.assertIsInstance(name, str)
            self.assertTrue(len(name) > 0)

    def test_required_features_present(self) -> None:
        """Key features from the Phase 4 spec must be in the list."""
        required = {
            "experience_years", "performance_rating", "skill_coverage_pct",
            "readiness_score", "skill_score", "cert_score",
            "experience_score", "project_score", "performance_score",
            "promotion_success" if "promotion_success" in FEATURE_NAMES else "readiness_score",
        }
        for feat in required - {"promotion_success"}:
            self.assertIn(feat, FEATURE_NAMES)

    def test_target_not_in_features(self) -> None:
        """TARGET_COLUMN must not appear in FEATURE_NAMES."""
        self.assertNotIn(TARGET_COLUMN, FEATURE_NAMES)


# ---------------------------------------------------------------------------
# TestSyntheticDatasetGenerator
# ---------------------------------------------------------------------------

class TestSyntheticDatasetGenerator(unittest.TestCase):
    """Tests for SyntheticDatasetGenerator."""

    def setUp(self) -> None:
        self.gen = SyntheticDatasetGenerator(SyntheticDatasetConfig(n_samples=200, random_seed=0))

    def test_output_shape(self) -> None:
        """DataFrame must have n_samples rows and 19 columns (18 features + target)."""
        df = self.gen.generate()
        self.assertEqual(df.shape, (200, 19))

    def test_all_feature_columns_present(self) -> None:
        """All 18 feature columns must be present."""
        df = self.gen.generate()
        for col in FEATURE_NAMES:
            self.assertIn(col, df.columns)

    def test_target_column_present(self) -> None:
        """promotion_success column must be present."""
        df = self.gen.generate()
        self.assertIn(TARGET_COLUMN, df.columns)

    def test_target_is_binary(self) -> None:
        """promotion_success must contain only 0 and 1."""
        df = self.gen.generate()
        unique = set(df[TARGET_COLUMN].unique())
        self.assertTrue(unique.issubset({0, 1}))

    def test_no_null_values(self) -> None:
        """Dataset must contain no NaN values."""
        df = self.gen.generate()
        self.assertEqual(df.isnull().sum().sum(), 0)

    def test_experience_years_range(self) -> None:
        """experience_years must be within [0.5, 20.0]."""
        df = self.gen.generate()
        self.assertGreaterEqual(df["experience_years"].min(), 0.5)
        self.assertLessEqual(df["experience_years"].max(), 20.0)

    def test_performance_rating_range(self) -> None:
        """performance_rating must be within [1.0, 5.0]."""
        df = self.gen.generate()
        self.assertGreaterEqual(df["performance_rating"].min(), 1.0)
        self.assertLessEqual(df["performance_rating"].max(), 5.0)

    def test_skill_coverage_pct_range(self) -> None:
        """skill_coverage_pct must be within [0.0, 100.0]."""
        df = self.gen.generate()
        self.assertGreaterEqual(df["skill_coverage_pct"].min(), 0.0)
        self.assertLessEqual(df["skill_coverage_pct"].max(), 100.0)

    def test_cert_completion_rate_range(self) -> None:
        """cert_completion_rate must be within [0.0, 1.0]."""
        df = self.gen.generate()
        self.assertGreaterEqual(df["cert_completion_rate"].min(), 0.0)
        self.assertLessEqual(df["cert_completion_rate"].max(), 1.0)

    def test_readiness_score_range(self) -> None:
        """readiness_score must be within [0.0, 100.0]."""
        df = self.gen.generate()
        self.assertGreaterEqual(df["readiness_score"].min(), 0.0)
        self.assertLessEqual(df["readiness_score"].max(), 100.0)

    def test_grade_gap_positive(self) -> None:
        """grade_gap must always be >= 1 (target grade > current grade)."""
        df = self.gen.generate()
        self.assertGreaterEqual(df["grade_gap"].min(), 1)

    def test_target_grade_greater_than_current(self) -> None:
        """target_grade_encoded must always be > current_grade_encoded."""
        df = self.gen.generate()
        self.assertTrue((df["target_grade_encoded"] > df["current_grade_encoded"]).all())

    def test_reproducibility(self) -> None:
        """Two generators with the same seed must produce identical DataFrames."""
        cfg = SyntheticDatasetConfig(n_samples=100, random_seed=99)
        df1 = SyntheticDatasetGenerator(cfg).generate()
        df2 = SyntheticDatasetGenerator(cfg).generate()
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_differ(self) -> None:
        """Different seeds must produce different datasets."""
        df1 = SyntheticDatasetGenerator(SyntheticDatasetConfig(n_samples=100, random_seed=1)).generate()
        df2 = SyntheticDatasetGenerator(SyntheticDatasetConfig(n_samples=100, random_seed=2)).generate()
        self.assertFalse(df1["readiness_score"].equals(df2["readiness_score"]))

    def test_class_balance_reasonable(self) -> None:
        """Promotion rate must be between 30% and 70% for a balanced dataset."""
        df = SyntheticDatasetGenerator(SyntheticDatasetConfig(n_samples=1000)).generate()
        rate = df[TARGET_COLUMN].mean()
        self.assertGreater(rate, 0.30)
        self.assertLess(rate, 0.70)

    def test_disclaimer_attribute(self) -> None:
        """DataFrame must carry the SYNTHETIC_DATA_DISCLAIMER attribute."""
        df = self.gen.generate()
        self.assertIn("disclaimer", df.attrs)
        self.assertEqual(df.attrs["disclaimer"], SYNTHETIC_DATA_DISCLAIMER)

    def test_scores_sum_to_readiness(self) -> None:
        """skill+cert+exp+proj+perf scores must sum to readiness_score (±0.1 rounding)."""
        df = self.gen.generate()
        computed = (
            df["skill_score"] + df["cert_score"] + df["experience_score"]
            + df["project_score"] + df["performance_score"]
        ).round(2)
        diff = (computed - df["readiness_score"]).abs()
        self.assertLess(diff.max(), 0.11)

    def test_custom_n_samples(self) -> None:
        """Generator must respect the n_samples configuration."""
        for n in (50, 500, 2000):
            df = SyntheticDatasetGenerator(SyntheticDatasetConfig(n_samples=n)).generate()
            self.assertEqual(len(df), n)


# ---------------------------------------------------------------------------
# TestFeatureEngineer
# ---------------------------------------------------------------------------

class TestFeatureEngineer(unittest.TestCase):
    """Tests for FeatureEngineer (live extraction from Phase 2/3 objects)."""

    def setUp(self) -> None:
        self.engineer = FeatureEngineer()
        self.employee = _make_employee()
        self.requirement = _make_requirement()
        self.gap = _make_gap_analysis(self.employee, self.requirement)
        self.result = _make_readiness_result(self.gap)

    def test_returns_feature_vector(self) -> None:
        """extract() must return a FeatureVector instance."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertIsInstance(fv, FeatureVector)

    def test_all_feature_names_present(self) -> None:
        """FeatureVector must contain all 18 feature names."""
        fv = self.engineer.extract(self.gap, self.result)
        for name in FEATURE_NAMES:
            self.assertIn(name, fv.features)

    def test_employee_id_set(self) -> None:
        """FeatureVector.employee_id must match the source employee."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertEqual(fv.employee_id, self.employee.employee_id)

    def test_to_numpy_shape(self) -> None:
        """to_numpy() must return a 1-D array of length 18."""
        fv = self.engineer.extract(self.gap, self.result)
        arr = fv.to_numpy()
        self.assertEqual(arr.shape, (18,))
        self.assertEqual(arr.dtype, np.float64)

    def test_to_dataframe_shape(self) -> None:
        """to_dataframe() must return a single-row DataFrame with 18 columns."""
        fv = self.engineer.extract(self.gap, self.result)
        df = fv.to_dataframe()
        self.assertEqual(df.shape, (1, 18))
        self.assertEqual(list(df.columns), FEATURE_NAMES)

    def test_experience_years_matches_employee(self) -> None:
        """experience_years feature must equal employee.experience_years."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertAlmostEqual(fv.features["experience_years"], self.employee.experience_years)

    def test_performance_rating_matches_employee(self) -> None:
        """performance_rating feature must equal employee.performance_rating."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertAlmostEqual(fv.features["performance_rating"], self.employee.performance_rating)

    def test_readiness_score_matches_result(self) -> None:
        """readiness_score feature must equal ReadinessResult.readiness_score."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertAlmostEqual(fv.features["readiness_score"], self.result.readiness_score)

    def test_skill_coverage_pct_range(self) -> None:
        """skill_coverage_pct must be in [0.0, 100.0]."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertGreaterEqual(fv.features["skill_coverage_pct"], 0.0)
        self.assertLessEqual(fv.features["skill_coverage_pct"], 100.0)

    def test_cert_completion_rate_range(self) -> None:
        """cert_completion_rate must be in [0.0, 1.0]."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertGreaterEqual(fv.features["cert_completion_rate"], 0.0)
        self.assertLessEqual(fv.features["cert_completion_rate"], 1.0)

    def test_grade_gap_positive(self) -> None:
        """grade_gap must be >= 1 when target grade is higher than current."""
        fv = self.engineer.extract(self.gap, self.result)
        self.assertGreaterEqual(fv.features["grade_gap"], 1.0)

    def test_no_skills_gives_zero_avg(self) -> None:
        """avg_skill_level must be 0.0 when employee has no skills."""
        emp = _make_employee(skills=[])
        gap = _make_gap_analysis(emp, self.requirement)
        result = _make_readiness_result(gap)
        fv = self.engineer.extract(gap, result)
        self.assertEqual(fv.features["avg_skill_level"], 0.0)

    def test_no_projects_gives_zero_avg_rating(self) -> None:
        """avg_project_rating must be 0.0 when employee has no projects."""
        emp = _make_employee(projects=[])
        gap = _make_gap_analysis(emp, self.requirement)
        result = _make_readiness_result(gap)
        fv = self.engineer.extract(gap, result)
        self.assertEqual(fv.features["avg_project_rating"], 0.0)

    def test_full_skill_coverage_no_gaps(self) -> None:
        """skill_coverage_pct must be 100.0 when employee meets all skill requirements."""
        emp = _make_employee(skills=[
            EmployeeSkill("Python", "Backend", 5),
            EmployeeSkill("AWS", "Cloud", 4),
        ])
        gap = _make_gap_analysis(emp, self.requirement)
        result = _make_readiness_result(gap)
        fv = self.engineer.extract(gap, result)
        self.assertAlmostEqual(fv.features["skill_coverage_pct"], 100.0)

    def test_mandatory_gap_count_correct(self) -> None:
        """mandatory_skill_gap_count must count only mandatory gaps."""
        # Python is mandatory, AWS is not — employee has neither
        emp = _make_employee(skills=[])
        gap = _make_gap_analysis(emp, self.requirement)
        result = _make_readiness_result(gap)
        fv = self.engineer.extract(gap, result)
        # Python is mandatory=True, AWS is mandatory=False → count = 1
        self.assertEqual(fv.features["mandatory_skill_gap_count"], 1.0)

    def test_no_cert_requirements_gives_full_rate(self) -> None:
        """cert_completion_rate must be 1.0 when grade has no cert requirements."""
        req = _make_requirement(certifications=[])
        gap = _make_gap_analysis(self.employee, req)
        result = _make_readiness_result(gap)
        fv = self.engineer.extract(gap, result)
        self.assertAlmostEqual(fv.features["cert_completion_rate"], 1.0)


# ---------------------------------------------------------------------------
# TestDataFrameFeatureEngineer
# ---------------------------------------------------------------------------

class TestDataFrameFeatureEngineer(unittest.TestCase):
    """Tests for DataFrameFeatureEngineer validation and preprocessing."""

    def setUp(self) -> None:
        self.eng = DataFrameFeatureEngineer()
        self.gen = SyntheticDatasetGenerator(SyntheticDatasetConfig(n_samples=100, random_seed=7))
        self.df = self.gen.generate()

    def test_validate_clean_returns_dataframe(self) -> None:
        """validate_and_clean() must return a DataFrame."""
        result = self.eng.validate_and_clean(self.df)
        self.assertIsInstance(result, pd.DataFrame)

    def test_validate_clean_preserves_shape(self) -> None:
        """validate_and_clean() must not change the number of rows or columns."""
        result = self.eng.validate_and_clean(self.df)
        self.assertEqual(result.shape, self.df.shape)

    def test_validate_clean_does_not_mutate_input(self) -> None:
        """validate_and_clean() must not modify the original DataFrame."""
        original_values = self.df["readiness_score"].copy()
        self.eng.validate_and_clean(self.df)
        pd.testing.assert_series_equal(self.df["readiness_score"], original_values)

    def test_clipping_out_of_range_values(self) -> None:
        """Out-of-range values must be clipped to valid bounds."""
        df = self.df.copy()
        df.loc[0, "readiness_score"] = 150.0   # above max 100
        df.loc[1, "readiness_score"] = -10.0   # below min 0
        df.loc[0, "performance_rating"] = 9.9  # above max 5
        result = self.eng.validate_and_clean(df)
        self.assertLessEqual(result["readiness_score"].max(), 100.0)
        self.assertGreaterEqual(result["readiness_score"].min(), 0.0)
        self.assertLessEqual(result["performance_rating"].max(), 5.0)

    def test_missing_column_raises_value_error(self) -> None:
        """validate_and_clean() must raise ValueError if a feature column is missing."""
        df_bad = self.df.drop(columns=["readiness_score"])
        with self.assertRaises(ValueError) as ctx:
            self.eng.validate_and_clean(df_bad)
        self.assertIn("readiness_score", str(ctx.exception))

    def test_get_X_y_shapes(self) -> None:
        """get_X_y() must return X with 18 columns and y with matching length."""
        X, y = self.eng.get_X_y(self.df)
        self.assertEqual(X.shape[1], 18)
        self.assertEqual(len(X), len(y))

    def test_get_X_y_column_order(self) -> None:
        """X columns must be in FEATURE_NAMES order."""
        X, _ = self.eng.get_X_y(self.df)
        self.assertEqual(list(X.columns), FEATURE_NAMES)

    def test_get_X_y_target_is_int(self) -> None:
        """y must have integer dtype."""
        _, y = self.eng.get_X_y(self.df)
        self.assertTrue(pd.api.types.is_integer_dtype(y))

    def test_get_X_y_missing_target_raises(self) -> None:
        """get_X_y() must raise ValueError if TARGET_COLUMN is absent."""
        df_no_target = self.df.drop(columns=[TARGET_COLUMN])
        with self.assertRaises(ValueError) as ctx:
            self.eng.get_X_y(df_no_target)
        self.assertIn(TARGET_COLUMN, str(ctx.exception))

    def test_get_X_y_no_target_in_X(self) -> None:
        """X must not contain the target column."""
        X, _ = self.eng.get_X_y(self.df)
        self.assertNotIn(TARGET_COLUMN, X.columns)


# ---------------------------------------------------------------------------
# TestDatasetBuilder
# ---------------------------------------------------------------------------

class TestDatasetBuilder(unittest.TestCase):
    """Tests for DatasetBuilder — uses a temporary directory to avoid side effects."""

    def _builder(self, n: int = 200, seed: int = 42) -> tuple[DatasetBuilder, Path]:
        tmp = tempfile.mkdtemp()
        path = Path(tmp) / "test_dataset.csv"
        cfg = SyntheticDatasetConfig(n_samples=n, random_seed=seed)
        return DatasetBuilder(output_path=path, config=cfg), path

    def test_build_and_save_creates_file(self) -> None:
        """build_and_save() must create the CSV file on disk."""
        builder, path = self._builder()
        builder.build_and_save()
        self.assertTrue(path.exists())

    def test_build_and_save_returns_dataframe(self) -> None:
        """build_and_save() must return a DataFrame."""
        builder, _ = self._builder()
        df = builder.build_and_save()
        self.assertIsInstance(df, pd.DataFrame)

    def test_build_and_save_correct_row_count(self) -> None:
        """Saved CSV must contain the expected number of data rows."""
        builder, path = self._builder(n=300)
        builder.build_and_save()
        # CSV has a disclaimer comment line + header + 300 data rows
        df = pd.read_csv(path, comment="#")
        self.assertEqual(len(df), 300)

    def test_csv_contains_disclaimer_comment(self) -> None:
        """First line of the CSV must be the disclaimer comment."""
        builder, path = self._builder()
        builder.build_and_save()
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        self.assertTrue(first_line.startswith("#"))
        self.assertIn("SYNTHETIC", first_line)

    def test_load_returns_X_y(self) -> None:
        """load() must return (X, y) with correct shapes."""
        builder, _ = self._builder(n=150)
        builder.build_and_save()
        X, y = builder.load()
        self.assertEqual(X.shape, (150, 18))
        self.assertEqual(len(y), 150)

    def test_load_X_columns_match_feature_names(self) -> None:
        """X returned by load() must have columns in FEATURE_NAMES order."""
        builder, _ = self._builder()
        builder.build_and_save()
        X, _ = builder.load()
        self.assertEqual(list(X.columns), FEATURE_NAMES)

    def test_load_raw_returns_full_dataframe(self) -> None:
        """load_raw() must return a DataFrame with features + target column."""
        builder, _ = self._builder(n=100)
        builder.build_and_save()
        df = builder.load_raw()
        self.assertIn(TARGET_COLUMN, df.columns)
        self.assertEqual(len(df), 100)

    def test_load_before_build_raises(self) -> None:
        """load() must raise FileNotFoundError if the dataset has not been built."""
        tmp = tempfile.mkdtemp()
        path = Path(tmp) / "nonexistent.csv"
        builder = DatasetBuilder(output_path=path)
        with self.assertRaises(FileNotFoundError):
            builder.load()

    def test_load_raw_before_build_raises(self) -> None:
        """load_raw() must raise FileNotFoundError if the dataset has not been built."""
        tmp = tempfile.mkdtemp()
        path = Path(tmp) / "nonexistent.csv"
        builder = DatasetBuilder(output_path=path)
        with self.assertRaises(FileNotFoundError):
            builder.load_raw()

    def test_dataset_path_property(self) -> None:
        """dataset_path property must return the configured output path."""
        builder, path = self._builder()
        self.assertEqual(builder.dataset_path, path)

    def test_reproducible_across_builds(self) -> None:
        """Two builds with the same seed must produce identical CSV content."""
        builder1, path1 = self._builder(n=100, seed=5)
        builder2, path2 = self._builder(n=100, seed=5)
        builder1.build_and_save()
        builder2.build_and_save()
        df1 = pd.read_csv(path1, comment="#")
        df2 = pd.read_csv(path2, comment="#")
        pd.testing.assert_frame_equal(df1, df2)

    def test_default_path_is_in_data_directory(self) -> None:
        """Default dataset_path must be inside the project's data/ directory."""
        builder = DatasetBuilder()
        self.assertEqual(builder.dataset_path.parent.name, "data")
        self.assertEqual(builder.dataset_path.name, "synthetic_progression_dataset.csv")


if __name__ == "__main__":
    unittest.main()
