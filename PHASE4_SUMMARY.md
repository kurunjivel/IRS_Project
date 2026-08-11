# IRS Phase 4 — ML Dataset + Feature Engineering
## Implementation Summary

---

## 1. Overview

Phase 4 converts the rule-based pipeline output from Phases 2 and 3 into a
machine-learning-ready dataset.  It answers the question:

> "What does a trainable, labelled dataset look like for predicting
>  employee promotion success?"

Phase 4 does **not** train any model.  That is Phase 5.

---

## 2. Data Disclaimer

> **SYNTHETIC ACADEMIC DATA — Not real HR data.**
> All records were generated programmatically for IRS demonstration and
> ML training purposes only.  No real employee, organisation, HR record,
> or promotion decision is represented.

This disclaimer is embedded as:
- A comment on the first line of every generated CSV file.
- A `df.attrs["disclaimer"]` attribute on every generated DataFrame.
- The `SYNTHETIC_DATA_DISCLAIMER` constant in `ml/synthetic_data_generator.py`.

---

## 3. Files Created

| File | Purpose |
|------|---------|
| `ml/__init__.py` | Package marker |
| `ml/synthetic_data_generator.py` | Generates the synthetic dataset |
| `ml/feature_engineering.py` | Extracts feature vectors from Phase 2/3 output |
| `ml/dataset_builder.py` | Orchestrates generation, validation, CSV persistence |
| `tests/test_phase4.py` | 61 unit tests |
| `data/synthetic_progression_dataset.csv` | Generated dataset (1 000 rows) |

---

## 4. Dataset Structure

```
data/synthetic_progression_dataset.csv
```

- First line: `# SYNTHETIC ACADEMIC DATA — ...` (disclaimer comment)
- Header row: 19 column names
- 1 000 data rows (configurable)

### Column layout

| # | Column | Type | Range | Description |
|---|--------|------|-------|-------------|
| 0 | experience_years | float | 0.5 – 20.0 | Total years of professional experience |
| 1 | performance_rating | float | 1.0 – 5.0 | Latest performance rating |
| 2 | skill_coverage_pct | float | 0.0 – 100.0 | % of required skills met or exceeded |
| 3 | avg_skill_level | float | 0.0 – 5.0 | Mean skill level across all held skills |
| 4 | mandatory_skill_gap_count | int | 0 – 10 | Number of mandatory skill gaps |
| 5 | cert_completion_rate | float | 0.0 – 1.0 | Fraction of required certs completed |
| 6 | project_completion_rate | float | 0.0 – 1.0 | Fraction of required projects completed |
| 7 | lead_project_completion_rate | float | 0.0 – 1.0 | Fraction of required lead projects completed |
| 8 | avg_project_rating | float | 0.0 – 5.0 | Mean rating across all projects |
| 9 | current_grade_encoded | int | 1 – 5 | Ordinal encoding of current grade |
| 10 | target_grade_encoded | int | 1 – 5 | Ordinal encoding of target grade |
| 11 | grade_gap | int | 1 – 2 | target_encoded − current_encoded |
| 12 | skill_score | float | 0.0 – 40.0 | Phase 3 skill readiness score |
| 13 | cert_score | float | 0.0 – 15.0 | Phase 3 certification readiness score |
| 14 | experience_score | float | 0.0 – 15.0 | Phase 3 experience readiness score |
| 15 | project_score | float | 0.0 – 20.0 | Phase 3 project readiness score |
| 16 | performance_score | float | 0.0 – 10.0 | Phase 3 performance readiness score |
| 17 | readiness_score | float | 0.0 – 100.0 | Phase 3 overall readiness score |
| 18 | **promotion_success** | int | **0 or 1** | **Target variable** |

---

## 5. Feature List (18 features)

```python
FEATURE_NAMES = [
    "experience_years",
    "performance_rating",
    "skill_coverage_pct",
    "avg_skill_level",
    "mandatory_skill_gap_count",
    "cert_completion_rate",
    "project_completion_rate",
    "lead_project_completion_rate",
    "avg_project_rating",
    "current_grade_encoded",
    "target_grade_encoded",
    "grade_gap",
    "skill_score",
    "cert_score",
    "experience_score",
    "project_score",
    "performance_score",
    "readiness_score",
]
```

`FEATURE_NAMES` is the **single source of truth** for column order.
Both training (Phase 5) and inference (Phase 7) use this constant to
guarantee the feature vector is always in the same order.

---

## 6. Target Variable

```
promotion_success  ∈  {0, 1}
```

| Value | Meaning |
|-------|---------|
| 0 | Employee did not successfully progress to the target grade |
| 1 | Employee successfully progressed to the target grade |

### Label derivation (synthetic)

The label is derived from `readiness_score` with added Gaussian noise
(σ = 8.0) to create a realistic, non-sharp decision boundary:

```
noisy_score = readiness_score + Normal(0, 8.0)
promotion_success = 1  if  noisy_score >= 65.0  else  0
```

The 65-point threshold is intentionally offset from Phase 3's 60-point
"Conditional" boundary so the ML model has something genuinely useful to
learn — some "Conditional" employees were promoted, some were not.

### Class balance (1 000 samples, seed 42)

| Class | Count | % |
|-------|-------|---|
| Promoted (1) | 612 | 61.2% |
| Not Promoted (0) | 388 | 38.8% |

---

## 7. Data Preprocessing Logic

### `SyntheticDatasetGenerator`

- Uses `numpy.random.default_rng(seed)` for full reproducibility.
- Grade pairs sampled from a configurable list; target always > current.
- Experience drawn from `Normal(current_grade × 2, 2.5)` — higher grades
  require more experience on average.
- Skill coverage drawn from `Beta(5, 2)` — right-skewed (most employees
  have reasonable coverage).
- Mandatory gap count inversely correlated with skill coverage via
  `Binomial(10, 1 − coverage)`.
- Lead project rate is a fraction of total project rate (realistic: fewer
  employees lead than participate).

### `DataFrameFeatureEngineer`

- `validate_and_clean(df)` — checks all 18 feature columns are present,
  clips each to its valid range, returns a copy (never mutates input).
- `get_X_y(df)` — splits into feature matrix X and target vector y,
  enforces integer dtype on y.

### `FeatureEngineer` (live inference)

- `extract(gap_analysis, readiness_result)` — pulls features directly
  from Phase 2 gap dicts and Phase 3 `ReadinessResult` dataclasses.
- Returns a `FeatureVector` with `.to_numpy()` and `.to_dataframe()` for
  immediate use with scikit-learn.

---

## 8. Sample Dataset Output

```
Rows        : 1,000
Features    : 18
Target      : promotion_success
Promoted    : 612  (61.2%)
Not Promoted: 388  (38.8%)

Readiness score by outcome:
                    mean    std    min    max
promotion_success
0                  61.20   7.31  39.10  82.45
1                  72.03   7.10  49.69  91.36
```

The mean readiness score for promoted employees (72.0) is clearly higher
than for non-promoted employees (61.2), confirming the dataset has a
learnable signal for Phase 5.

---

## 9. Unit Tests

**File:** `tests/test_phase4.py`
**Total:** 61 tests — all passing

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestFeatureNames` | 5 | FEATURE_NAMES contract, count, uniqueness, no target leakage |
| `TestSyntheticDatasetGenerator` | 18 | Shape, dtypes, ranges, balance, reproducibility, disclaimer, score sums |
| `TestFeatureEngineer` | 16 | Live extraction, all features, edge cases (no skills, no projects, no certs) |
| `TestDataFrameFeatureEngineer` | 10 | Validation, clipping, get_X_y, error paths |
| `TestDatasetBuilder` | 12 | Build, save, load, load_raw, FileNotFoundError, reproducibility, paths |

---

## 10. Running Phase 4

### Generate the dataset

```bash
# Default: 1 000 rows, seed 42
python -m ml.dataset_builder

# Custom sample count
python -m ml.dataset_builder 5000
```

Output: `data/synthetic_progression_dataset.csv`

### Run Phase 4 tests only

```bash
python -m unittest tests/test_phase4.py -v
```

### Run all tests (Phase 2 + 3 + 4)

```bash
python -m unittest discover -s tests -v
```

Expected: **132 tests, 0 failures**

### Use from code (Phase 5 will call this)

```python
from ml.dataset_builder import DatasetBuilder

builder = DatasetBuilder()
X, y = builder.load()          # loads saved CSV → (DataFrame, Series)
print(X.shape)                 # (1000, 18)
print(y.value_counts())        # 1: 612,  0: 388
```

### Extract features for a live employee (Phase 7 will call this)

```python
from ml.feature_engineering import FeatureEngineer

engineer = FeatureEngineer()
fv = engineer.extract(gap_analysis, readiness_result)
X  = fv.to_numpy().reshape(1, -1)   # ready for model.predict_proba(X)
```

---

## 11. ML Safety Notes

- No protected or sensitive personal attributes are included in the
  feature set (no race, gender, religion, health, etc.).
- All features are job-relevant: skills, experience, performance,
  projects, certifications.
- The `promotion_success` label is derived from job-relevant readiness
  scores only.
- ML prediction is advisory — it must not automatically make employment
  decisions.  Human/HR review remains necessary.

---

## 12. What Phase 5 Will Build On

Phase 5 (ML Promotion Prediction Model) will:

1. Call `DatasetBuilder().load()` to get `(X, y)`.
2. Split into train/validation/test sets.
3. Train Logistic Regression, Decision Tree, and Random Forest classifiers.
4. Evaluate using Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix.
5. Select the best model based on test-set performance.
6. Save the trained model with `joblib` to `models/promotion_model.pkl`.
7. Expose `predict_proba(feature_vector)` for use in Phase 6 and Phase 7.
