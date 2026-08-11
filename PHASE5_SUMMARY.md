# IRS Phase 5 — Machine Learning Promotion Progression Prediction Model
## Implementation Summary

---

## 1. Objective

Phase 5 trains, compares, and persists a supervised binary classification model
that predicts whether an employee is likely to successfully progress to their
target grade.

**Input**: 26 ML-ready features from Phase 4  
**Output**: `promotion_probability` ∈ [0, 1] and `prediction` ∈ {"Likely Progression", "Unlikely Progression"}

---

## 2. Data Disclaimer

> **SYNTHETIC ACADEMIC DATA — Not real HR data.**  
> The dataset used for training was generated programmatically for IRS
> demonstration and ML training purposes only. It does NOT represent any real
> employee, organisation, HR record, or promotion decision.

---

## 3. Architecture

```
datasets/historical_employee_progression.csv
          │
          ▼
services/ml/data_preprocessor.py
    DataPreprocessor.load_and_split()
          │  ┌─ duplicate removal
          │  ├─ missing-value imputation (median)
          │  ├─ numeric range clipping
          │  └─ 80/20 stratified train/test split
          │
          ▼
services/ml/model_trainer.py
    ModelTrainer.train()
          │  ┌─ LogisticRegression
          │  ├─ DecisionTreeClassifier
          │  └─ RandomForestClassifier
          │  └─ (XGBoost if installed)
          │
          ├── 5-fold StratifiedKFold cross-validation on training set
          ├── Best model selected by CV F1-macro (ties broken by ROC-AUC)
          └── Best model refitted on full training set → saved to ml_models/
          │
          ▼
services/ml/model_evaluator.py
    ModelEvaluator.evaluate()
          │  ┌─ Accuracy, Precision, Recall, F1 (macro)
          │  ├─ ROC-AUC
          │  └─ Confusion Matrix + Classification Report
          │
          ▼
services/ml/predictor.py
    Predictor.predict(feature_row)
          └─ Returns structured dict with required output schema
```

---

## 4. Dataset (Phase 4 Output)

| Property | Value |
|----------|-------|
| File | `datasets/historical_employee_progression.csv` |
| Rows | 1,200 (synthetic, seed=42) |
| Features | 26 (see Section 6) |
| Target | `promotion_success` ∈ {0, 1} |
| Positive class (promoted) | 651 (54.2%) |
| Negative class (not promoted) | 549 (45.8%) |
| Train rows | 960 (80%) |
| Test rows | 240 (20%) |
| Positive (train) | 521 |
| Negative (train) | 439 |
| Positive (test) | 130 |
| Negative (test) | 110 |
| Random state | 42 |

**Note:** The dataset was regenerated with an improved label generation formula
that produces a balanced ~54/46 class distribution (down from 72/28 in the
first run). A `−0.40` bias term was added to the logit to centre the sigmoid
output, producing a more realistic and learnable boundary.

---

## 5. Feature Set (26 Features)

### Employee Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `experience_years` | float | 0.5–20.0 | Total years of professional experience |
| `performance_rating` | float | 1.0–5.0 | Latest performance rating |
| `current_grade_encoded` | int | 1–5 | Ordinal encoding of current grade (G1=1…G5=5) |
| `target_grade_encoded` | int | 1–5 | Ordinal encoding of target grade |
| `grade_gap` | int | 1–4 | target_encoded − current_encoded |

### Skill Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `total_skills` | int | 2–15 | Total skills held |
| `average_skill_level` | float | 0.0–5.0 | Mean skill level across all skills |
| `skill_coverage_percentage` | float | 0.0–100.0 | % of required skills met or exceeded |
| `mandatory_skill_gap_count` | int | 0–8 | Count of mandatory skill gaps |
| `weighted_skill_gap` | float | ≥0 | Sum of (gap_levels × weight) for all gaps |

### Certification Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `total_certifications` | int | 0–6 | Total certifications held |
| `completed_certifications` | int | 0–6 | Certifications with status=Completed |
| `certification_completion_rate` | float | 0.0–1.0 | completed / total_required |
| `mandatory_certification_gap_count` | int | 0–3 | Count of mandatory cert gaps |

### Project Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `total_projects` | int | 0–10 | Total projects participated in |
| `completed_projects` | int | 0–10 | All listed projects (alias for total_projects) |
| `lead_projects` | int | 0–5 | Projects where employee was lead |
| `project_completion_rate` | float | 0.0–1.0 | total_projects / required_projects |
| `lead_project_completion_rate` | float | 0.0–1.0 | lead_projects / required_lead_projects |
| `average_project_rating` | float | 0.0–5.0 | Mean project rating |

### Readiness Score Features (Phase 3)
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `skill_score` | float | 0.0–40.0 | Phase 3 skill readiness score |
| `certification_score` | float | 0.0–15.0 | Phase 3 certification readiness score |
| `experience_score` | float | 0.0–15.0 | Phase 3 experience readiness score |
| `project_score` | float | 0.0–20.0 | Phase 3 project readiness score |
| `performance_score` | float | 0.0–10.0 | Phase 3 performance readiness score |
| `readiness_score` | float | 0.0–100.0 | Phase 3 overall readiness score |

---

## 6. Grade Encoding

Grades are encoded ordinally as integers, NOT treated as continuous:

| Grade | Encoding |
|-------|----------|
| G1 | 1 |
| G2 | 2 |
| G3 | 3 |
| G4 | 4 |
| G5 | 5 |

The `grade_gap` feature (target_encoded − current_encoded) captures the distance
between current and target grades as a meaningful ordinal feature, ensuring
the model understands the magnitude of the progression step.

---

## 7. Target Variable

```
promotion_success ∈ {0, 1}
```

| Value | Meaning |
|-------|---------|
| 0 | Employee did not successfully progress to the target grade |
| 1 | Employee successfully progressed to the target grade |

### Label Derivation (Synthetic — Anti-Leakage Design)

The label is **NOT** derived by thresholding `readiness_score` directly (which
would cause target leakage — the ML model would just learn to reproduce the
Phase 3 formula). Instead:

```
logit = (
    0.30 × norm(experience_years)
  + 0.25 × norm(performance_rating)
  + 0.20 × norm(skill_coverage_percentage)
  + 0.15 × norm(project_completion_rate)
  + 0.10 × norm(lead_project_completion_rate)
  − 0.20 × norm(mandatory_skill_gap_count)
  − 0.15 × norm(mandatory_certification_gap_count)
  − 0.40   ← bias: centres distribution → ~55% positive rate
  + Noise(0, 0.60)
)

probability = sigmoid(logit × 3)
promotion_success = Bernoulli(probability)
```

This ensures:
- The label reflects multiple independent raw factors
- It is NOT a deterministic function of `readiness_score`
- The ML model must learn a pattern from the data
- Noise prevents a perfectly sharp decision boundary

---

## 8. Model Training

### Models Trained

| # | Model | Configuration |
|---|-------|---------------|
| 1 | `LogisticRegression` | max_iter=1000, class_weight='balanced', StandardScaler |
| 2 | `DecisionTreeClassifier` | max_depth=8, min_samples_leaf=10, class_weight='balanced' |
| 3 | `RandomForestClassifier` | n_estimators=200, max_depth=10, min_samples_leaf=5, class_weight='balanced' |
| 4 | `XGBClassifier` | n_estimators=200, max_depth=6, lr=0.1 — *only if xgboost is installed* |

All models are wrapped in a `Pipeline` with `StandardScaler → Classifier`.

### Cross-Validation

- **Method**: StratifiedKFold (5 folds), preserves class balance in each fold
- **Primary metric**: F1-macro (penalises class imbalance)
- **Tie-breaking**: ROC-AUC
- **Random state**: 42

### Model Selection Criterion

Best model is chosen by **CV F1-macro on the training set**, NOT test-set
accuracy. F1-macro is preferred because:
- It equally weighs both classes regardless of prevalence
- Accuracy can be misleading with even moderate class imbalance

---

## 9. Model Comparison Table (Cross-Validation Results)

| Model | CV F1 (macro) | CV Accuracy | CV ROC-AUC | Selected |
|-------|--------------|-------------|------------|----------|
| LogisticRegression | 0.5324 | 0.5344 | 0.5536 | ✓ |
| RandomForestClassifier | 0.5323 | 0.5385 | 0.5446 | |
| DecisionTreeClassifier | 0.5177 | 0.5229 | 0.5334 | |

**Selected model**: `LogisticRegression` (best CV F1-macro)

---

## 10. Test-Set Evaluation Results

### LogisticRegression (Best Model — Saved)

| Metric | Value |
|--------|-------|
| Accuracy | 0.5833 |
| Precision (macro) | 0.5865 |
| Recall (macro) | 0.5867 |
| F1 (macro) | 0.5833 |
| ROC-AUC | 0.6010 |

**Confusion Matrix** (rows = actual, cols = predicted):

|  | Pred: Not Promoted | Pred: Promoted |
|--|-------------------|----------------|
| **Actual: Not Promoted** | 69 (TN) | 41 (FP) |
| **Actual: Promoted** | 59 (FN) | 71 (TP) |

### RandomForestClassifier

| Metric | Value |
|--------|-------|
| Accuracy | 0.5917 |
| Precision (macro) | 0.5884 |
| Recall (macro) | 0.5881 |
| F1 (macro) | 0.5882 |
| ROC-AUC | 0.6018 |

### DecisionTreeClassifier

| Metric | Value |
|--------|-------|
| Accuracy | 0.4542 |
| Precision (macro) | 0.4612 |
| Recall (macro) | 0.4626 |
| F1 (macro) | 0.4520 |
| ROC-AUC | 0.4460 |

> **Note on performance**: The F1 scores (~0.53–0.59) are modest, which is
> expected for synthetic data with intentional noise in the label-generation
> process. The noise was deliberately added to prevent the model from memorising
> the Phase 3 formula. Real HR data with genuine historical promotion records
> would yield substantially higher scores.

---

## 11. Saved Model and Artifacts

| File | Description |
|------|-------------|
| `ml_models/promotion_model.pkl` | Fitted `Pipeline` (StandardScaler + LogisticRegression) |
| `ml_models/model_metadata.json` | Model name, feature columns, CV metrics, hyperparameters |

### Prediction Output Schema

```json
{
    "employee_id":           101,
    "current_grade":         "G2",
    "target_grade":          "G3",
    "promotion_probability": 0.87,
    "prediction":            "Likely Progression",
    "model_name":            "LogisticRegression"
}
```

**Decision threshold**: 0.50 (configurable via `Predictor(threshold=...)`).

---

## 12. Data Leakage Prevention

The following fields are **explicitly excluded** from the feature set to prevent
information leakage:

| Excluded Field | Reason |
|----------------|--------|
| Future promotion date | Not available at prediction time |
| Post-promotion grade | Future information |
| Post-promotion performance rating | Future information |
| Projects completed after promotion | Future information |
| Certifications completed after promotion | Future information |

Only information available at the **time of the promotion decision** is used.

---

## 13. Preprocessing Pipeline

| Step | Action |
|------|--------|
| Load | Read CSV (skip `#` comment lines) |
| Deduplication | Remove exact duplicate rows (log count) |
| Missing values | Impute with column median (log each affected column) |
| Range clipping | Clip each feature to its valid range (documented in `DataPreprocessor._clip_ranges`) |
| Separation | Split into X (26 features) and y (target) |
| Train/test split | 80/20 stratified split, `random_state=42` |

---

## 14. Files Created

| File | Purpose |
|------|---------|
| `services/ml/model_trainer.py` | ModelTrainer: trains, compares, selects, saves |
| `services/ml/model_evaluator.py` | ModelEvaluator: computes all test-set metrics |
| `services/ml/predictor.py` | Predictor: loads model, generates predictions |
| `ml_models/promotion_model.pkl` | Saved best model pipeline |
| `ml_models/model_metadata.json` | Model metadata and CV results |
| `tests/test_ml_model.py` | 66 unit tests covering all Phase 5 components |
| `PHASE5_SUMMARY.md` | This document |

### Files Modified

| File | Change |
|------|--------|
| `services/ml/dataset_generator.py` | Added `−0.40` bias + σ=0.60 noise to `_derive_labels` for ~55/45 class balance; increased default n_samples to 1,200 |

---

## 15. Tests

**File**: `tests/test_ml_model.py`  
**Total**: 66 tests — all passing

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestModelTraining` | 11 | Training report, CV scores, model selection, paths |
| `TestModelLoading` | 9 | Pickle load, pipeline structure, metadata, reload |
| `TestPrediction` | 8 | Single, batch, dict/Series/DataFrame inputs |
| `TestProbabilityRange` | 6 | [0,1] bounds, float type, 4dp precision, threshold |
| `TestOutputSchema` | 11 | Required keys, types, defaults, no extra keys |
| `TestInvalidInput` | 8 | Missing features, wrong type, bad threshold, missing file |
| `TestModelPersistence` | 7 | PKL exists, round-trip, custom path, file size, metadata |
| `TestModelEvaluator` | 13 | All metrics, confusion matrix shape, comparison table |

---

## 16. How to Run

### Regenerate dataset and retrain model

```bash
# From project root:

# Regenerate the CSV dataset (1,200 rows, seed=42)
python -c "
from services.ml.dataset_generator import DatasetGenerator
gen = DatasetGenerator()
gen.save()
"

# Retrain all models and save best
python train_phase5.py
```

### Run Phase 5 tests only

```bash
python -m pytest tests/test_ml_model.py -v
```

### Run all tests (Phase 2 + 3 + 4 + 5)

```bash
python -m pytest tests/ -v
```

Expected: **208 tests, 0 failures**

### Make a prediction

```python
from services.ml.predictor import Predictor
from services.ml.feature_engineering import FEATURE_COLUMNS

predictor = Predictor()

# Build a feature dict (all 26 features)
features = {col: 0.0 for col in FEATURE_COLUMNS}
features.update({
    "experience_years": 8.0,
    "performance_rating": 4.2,
    "current_grade_encoded": 2.0,
    "target_grade_encoded": 3.0,
    "grade_gap": 1.0,
    "skill_coverage_percentage": 85.0,
    "certification_completion_rate": 0.75,
    "readiness_score": 72.0,
    # ... etc.
})

result = predictor.predict(
    features,
    employee_id=101,
    current_grade="G2",
    target_grade="G3",
)
print(result)
# {
#   "employee_id": 101,
#   "current_grade": "G2",
#   "target_grade": "G3",
#   "promotion_probability": 0.63,
#   "prediction": "Likely Progression",
#   "model_name": "LogisticRegression"
# }
```

---

## 17. What Phase 6 Will Build On

Phase 6 (API / Service Layer) will:

1. Expose `/predict` REST endpoint that accepts employee features and returns
   the prediction JSON.
2. Call `Predictor().predict(feature_dict)` under the hood.
3. Integrate with the Phase 2 + Phase 3 pipeline for end-to-end employee
   promotion readiness assessment.

---

## 18. ML Safety Notes

- No protected or sensitive personal attributes (race, gender, religion,
  health, age, etc.) are included in the feature set.
- All features are job-relevant: skills, experience, performance, projects,
  certifications.
- The `promotion_success` label is derived from job-relevant factors only.
- ML prediction is **advisory** — it must NOT automatically make employment
  decisions. Human/HR review remains necessary.
- The model is trained on synthetic data and should be validated against real
  historical data before any production use.
