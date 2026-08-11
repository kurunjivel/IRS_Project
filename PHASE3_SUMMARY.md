# IRS Phase 3 — Readiness Scoring Engine
## Implementation Summary

---

## 1. Overview

Phase 3 builds directly on top of the Phase 2 Gap Analysis Engine.
It consumes the gap analysis output — without touching the database or any
repository layer — and converts it into a structured Promotion Readiness Report.

The report answers one question:

> "How prepared is this employee for promotion to their target grade?"

The answer is expressed as:

- An **Overall Readiness Score** (0 – 100)
- A **Readiness Level** (human-readable label)
- A **Promotion Decision** (Ready / Conditional / Not Ready)
- A **Detailed Score Breakdown** per category

Phase 3 does **not** recommend courses, mentors, certifications, or projects.
That belongs to Phase 4.

---

## 2. Project Structure Added

```
IRS_Project/
├── services/
│   └── readiness/                         ← NEW Phase 3 package
│       ├── __init__.py
│       ├── skill_score_service.py
│       ├── certification_score_service.py
│       ├── experience_score_service.py
│       ├── project_score_service.py
│       ├── performance_score_service.py
│       ├── readiness_engine.py
│       └── readiness_report.py
├── tests/
│   ├── test_gap_analysis.py               ← Phase 2 (unchanged)
│   └── test_readiness.py                  ← NEW Phase 3 tests
└── main.py                                ← Updated to chain Phase 2 → Phase 3
```

---

## 3. Scoring Weights

All five categories contribute to a single 100-point score.

| Category        | Max Points | Weight |
|-----------------|-----------|--------|
| Skills          | 40        | 40%    |
| Projects        | 20        | 20%    |
| Experience      | 15        | 15%    |
| Certifications  | 15        | 15%    |
| Performance     | 10        | 10%    |
| **TOTAL**       | **100**   | **100%** |

Weights are stored as module-level float constants in `readiness_engine.py`
(`WEIGHT_SKILLS`, `WEIGHT_PROJECTS`, `WEIGHT_EXPERIENCE`,
`WEIGHT_CERTIFICATIONS`, `WEIGHT_PERFORMANCE`) and are also embedded in
each individual service file as `*_MAX_SCORE` constants for single-source
clarity.

---

## 4. File-by-File Implementation Detail

---

### 4.1 `skill_score_service.py`

**Responsibility:** Score the employee's skills against the target grade's
skill requirements.

**Constant:** `SKILL_MAX_SCORE = 40.0`

**Dataclass returned:** `SkillScoreResult`

| Field           | Type        | Description                                      |
|-----------------|-------------|--------------------------------------------------|
| `score`         | `float`     | Points earned (0 – 40)                           |
| `max_score`     | `float`     | Always 40.0                                      |
| `percentage`    | `float`     | `score / 40 × 100`                               |
| `missing_skills`| `list[str]` | Names of skills the employee does not hold at all|

**Scoring logic:**

Each required skill is worth an equal share of 40 points
(`40 / number_of_required_skills`).

For every required skill:

- If the skill is **not in the gap list** → employee meets or exceeds the
  requirement → full points awarded for that slot.
- If the skill **is in the gap list** with `current_level == 0` → skill is
  entirely missing → 0 points, name added to `missing_skills`.
- If the skill **is in the gap list** with `current_level > 0` → partial
  credit: `points_per_skill × (current_level / required_level)`.

**Edge case:** If the grade has no skill requirements, the full 40 points
are awarded automatically.

**Input consumed from Phase 2:** `skill_gaps` list (from `SkillGapService`).

**Gap map lookup** is built as a `dict[str, dict]` keyed by lowercase skill
name for O(1) access per skill.

---

### 4.2 `certification_score_service.py`

**Responsibility:** Score the employee's completed certifications against
the target grade's certification requirements.

**Constant:** `CERTIFICATION_MAX_SCORE = 15.0`

**Dataclass returned:** `CertificationScoreResult`

| Field       | Type        | Description                                        |
|-------------|-------------|----------------------------------------------------|
| `score`     | `float`     | Points earned (0 – 15)                             |
| `max_score` | `float`     | Always 15.0                                        |
| `completed` | `int`       | Number of required certifications the employee holds|
| `missing`   | `list[str]` | Names of missing certifications                    |

**Scoring logic:**

Each required certification is worth an equal share of 15 points
(`15 / total_required`).

- Certifications present in the `certification_gaps` list are missing → 0
  points for those slots.
- Certifications not in the gap list are completed → full points per slot.

`completed_count = total_required − missing_count`

`score = completed_count × points_per_cert`

**Edge case:** If the grade has no certification requirements, the full 15
points are awarded automatically.

**Input consumed from Phase 2:** `certification_gaps` list
(from `CertificationGapService`). A certification only counts as completed
if its status is `"Completed"` — this rule is enforced by Phase 2, not
re-evaluated here.

---

### 4.3 `experience_score_service.py`

**Responsibility:** Score the employee's years of experience against the
minimum experience required by the target grade.

**Constant:** `EXPERIENCE_MAX_SCORE = 15.0`

**Dataclass returned:** `ExperienceScoreResult`

| Field            | Type    | Description                              |
|------------------|---------|------------------------------------------|
| `current_years`  | `float` | Employee's total experience              |
| `required_years` | `float` | Grade's minimum experience requirement   |
| `gap_years`      | `float` | Remaining years needed (always ≥ 0)      |
| `score`          | `float` | Points earned (0 – 15)                   |

**Formula:**

```
ratio = min(current_years / required_years, 1.0)
score = round(ratio × 15, 2)
```

Score is **capped at 15** — exceeding the requirement does not yield bonus
points.

**Edge case:** If `required_years == 0.0`, the full 15 points are awarded.

**Input consumed from Phase 2:** `experience_gap` dict
(from `ExperienceGapService`), keys: `current_years`, `required_years`,
`remaining_years`.

---

### 4.4 `project_score_service.py`

**Responsibility:** Score the employee's project participation (total
projects and lead projects) against the target grade's project requirements.

**Constant:** `PROJECT_MAX_SCORE = 20.0`

**Internal split:**

| Sub-category    | Share of 20 pts | Constant        |
|-----------------|-----------------|-----------------|
| Total projects  | 14 pts (70%)    | `_TOTAL_WEIGHT` |
| Lead projects   | 6 pts (30%)     | `_LEAD_WEIGHT`  |

**Dataclass returned:** `ProjectScoreResult`

| Field            | Type    | Description                              |
|------------------|---------|------------------------------------------|
| `completed`      | `int`   | Total projects the employee has done     |
| `required`       | `int`   | Minimum total projects required          |
| `remaining`      | `int`   | Projects still needed (≥ 0)              |
| `lead_completed` | `int`   | Lead projects the employee has done      |
| `lead_required`  | `int`   | Minimum lead projects required           |
| `lead_remaining` | `int`   | Lead projects still needed (≥ 0)         |
| `score`          | `float` | Combined points earned (0 – 20)          |

**Formula:**

```
total_score = min(total_done / total_req, 1.0) × 14
lead_score  = min(lead_done  / lead_req,  1.0) × 6
score       = round(total_score + lead_score, 2)
```

Both sub-scores are independently capped — exceeding either requirement
does not yield bonus points.

**Edge cases:** If either requirement is 0, the full sub-score for that
category is awarded automatically.

**Input consumed from Phase 2:** `project_gap` dict
(from `ProjectGapService`).

---

### 4.5 `performance_score_service.py`

**Responsibility:** Score the employee's performance rating.

**Constants:**
- `PERFORMANCE_MAX_SCORE = 10.0`
- `PERFORMANCE_RATING_MAX = 5.0`

**Dataclass returned:** `PerformanceScoreResult`

| Field                | Type    | Description                          |
|----------------------|---------|--------------------------------------|
| `performance_rating` | `float` | Clamped rating (0.0 – 5.0)           |
| `score`              | `float` | Points earned (0 – 10)               |

**Formula:**

```
rating = clamp(employee.performance_rating, 0.0, 5.0)
score  = round((rating / 5.0) × 10, 2)
```

The rating is clamped with `max(0.0, min(rating, 5.0))` to guard against
out-of-range database values.

**Input consumed from Phase 2:** `employee.performance_rating` directly
from the `Employee` object.

---

### 4.6 `readiness_engine.py`

**Responsibility:** Orchestrate all five scoring services and combine their
results into a single `ReadinessResult`.

**Weight constants (module-level):**

```python
WEIGHT_SKILLS          = 40.0
WEIGHT_PROJECTS        = 20.0
WEIGHT_EXPERIENCE      = 15.0
WEIGHT_CERTIFICATIONS  = 15.0
WEIGHT_PERFORMANCE     = 10.0
```

**Dataclasses:**

`ReadinessBreakdown` — holds one result object per category plus the
weights dict.

`ReadinessResult` — holds the final `readiness_score` (float) and the
full `ReadinessBreakdown`.

**Class: `ReadinessEngine`**

- Instantiates all five scoring services in `__init__`.
- Single public method: `calculate(gap_analysis: dict) → ReadinessResult`
- Extracts `employee` and `requirement` from the gap analysis dict.
- Calls each service in sequence.
- Sums all five scores and rounds to 2 decimal places.
- Does **not** access the database or any repository.

**Data flow:**

```
gap_analysis dict (from Phase 2)
        │
        ├─ skill_gaps          → SkillScoreService.calculate()
        ├─ certification_gaps  → CertificationScoreService.calculate()
        ├─ experience_gap      → ExperienceScoreService.calculate()
        ├─ project_gap         → ProjectScoreService.calculate()
        └─ employee            → PerformanceScoreService.calculate()
                                        │
                                        ▼
                               ReadinessResult
                          (readiness_score + breakdown)
```

---

### 4.7 `readiness_report.py`

**Responsibility:** Convert a `ReadinessResult` into a fully structured,
JSON-serialisable `ReadinessReport` with a human-readable level and
promotion decision.

**Readiness Level mapping:**

| Score Range | Level              |
|-------------|--------------------|
| 90 – 100    | Promotion Ready    |
| 75 – 89     | Almost Ready       |
| 60 – 74     | Needs Improvement  |
| 40 – 59     | Significant Gaps   |
| 0 – 39      | Not Ready          |

Thresholds are stored as a sorted `list[tuple[float, str]]` (`_LEVELS`)
and resolved by iterating from highest to lowest — the first threshold the
score meets or exceeds wins.

**Promotion Decision mapping:**

| Score Range | Decision    |
|-------------|-------------|
| ≥ 90        | Ready       |
| 60 – 89     | Conditional |
| < 60        | Not Ready   |

**Dataclass returned:** `ReadinessReport`

| Field               | Type    | Description                                  |
|---------------------|---------|----------------------------------------------|
| `employee`          | `dict`  | Key employee fields (id, name, grades, etc.) |
| `readiness_score`   | `float` | Overall score (0 – 100)                      |
| `readiness_level`   | `str`   | Human-readable level label                   |
| `promotion_decision`| `str`   | Ready / Conditional / Not Ready              |
| `breakdown`         | `dict`  | Per-category score, max, gap details, weight |

**Class: `ReadinessReportBuilder`**

- Single public method: `build(employee, result) → ReadinessReport`
- Three private static helpers:
  - `_resolve_level(score)` — maps score to level string
  - `_resolve_decision(score)` — maps score to decision string
  - `_build_employee_dict(employee)` — serialises employee fields
  - `_build_breakdown(result)` — serialises all five category breakdowns

---

### 4.8 `main.py` (Updated)

The entry point now runs both phases in sequence for a given employee ID.

**Flow:**

```
python main.py <employee_id>
        │
        ▼
Phase 2 — GapAnalysisService.run(employee_id)
        │  returns gap_analysis dict
        ▼
Print Phase 2 Gap Analysis Report (JSON)
        │
        ▼
Phase 3 — ReadinessEngine.calculate(gap_analysis)
        │  returns ReadinessResult
        ▼
ReadinessReportBuilder.build(employee, result)
        │  returns ReadinessReport
        ▼
Print Phase 3 Promotion Readiness Report (JSON)
```

Error handling covers `EmployeeNotFoundError`, `GradeNotFoundError`, and
any unexpected exception. The database connection pool is always released
in the `finally` block.

---

## 5. Design Decisions

### 5.1 No direct database access from scoring services
All scoring services receive plain Python objects (`Employee`,
`GradeRequirement`, gap dicts). The database is only touched by Phase 2's
`DataLoader` and repositories. This enforces a clean separation of concerns
and makes every scoring service independently testable without a database.

### 5.2 Gap analysis output is the single source of truth
Phase 3 does not re-run any gap logic. It trusts the gap analysis dict
produced by Phase 2 entirely. This avoids duplication and ensures
consistency between the gap report and the readiness score.

### 5.3 Scores are capped, never bonus
Every formula uses `min(ratio, 1.0)` before multiplying by the max score.
Exceeding a requirement (e.g., 10 years experience when 5 are required)
does not inflate the score beyond the category maximum.

### 5.4 Partial credit for skills
Unlike certifications (binary: held or not), skills use proportional
scoring. An employee with level 3 out of a required level 5 earns 60% of
that skill's point allocation. This rewards partial progress.

### 5.5 Project score is internally split
The 20-point project budget is split 70/30 between total projects and lead
projects. This rewards both breadth of participation and leadership
experience independently.

### 5.6 SOLID principles applied
- **S** — Each service has exactly one scoring responsibility.
- **O** — New scoring categories can be added without modifying existing
  services.
- **L** — All result dataclasses are substitutable without breaking the
  engine.
- **I** — No service is forced to implement methods it does not need.
- **D** — `ReadinessEngine` depends on service abstractions, not concrete
  database calls.

### 5.7 Dataclasses used throughout
All result types (`SkillScoreResult`, `CertificationScoreResult`,
`ExperienceScoreResult`, `ProjectScoreResult`, `PerformanceScoreResult`,
`ReadinessBreakdown`, `ReadinessResult`, `ReadinessReport`) are Python
`@dataclass` instances. This provides type safety, auto-generated `__repr__`,
and clean field access without boilerplate.

---

## 6. Unit Tests — `tests/test_readiness.py`

**Total tests: 27 | Result: 27 passed, 0 failed**

### Test classes and coverage

| Test Class                    | Tests | What is covered                                      |
|-------------------------------|-------|------------------------------------------------------|
| `TestSkillScoreService`       | 4     | Full score, zero score, partial score, no requirements|
| `TestCertificationScoreService`| 3    | Full score, zero score, partial score                |
| `TestExperienceScoreService`  | 3     | Full score, partial score, score capped at max       |
| `TestProjectScoreService`     | 3     | Full score, zero score, partial score                |
| `TestPerformanceScoreService` | 3     | Max rating, zero rating, proportional score          |
| `TestReadinessEngine`         | 6     | All 6 required integration scenarios (see below)    |
| `TestReadinessReportBuilder`  | 5     | All 5 readiness level + decision mappings            |

### 6 Required Integration Scenarios (TestReadinessEngine)

| # | Test                          | What is asserted                                              |
|---|-------------------------------|---------------------------------------------------------------|
| 1 | `test_fully_eligible_employee`| Score = 100.0, level = "Promotion Ready", decision = "Ready" |
| 2 | `test_missing_one_skill`      | Score < 100, skill score > 0 (partial credit applied)        |
| 3 | `test_missing_certifications` | Certification score = 0, overall score < 100                 |
| 4 | `test_missing_experience`     | Experience score < 15, overall score < 100                   |
| 5 | `test_missing_projects`       | Project score = 0, overall score < 100                       |
| 6 | `test_poor_performance`       | Performance score < 10, decision is "Ready" or "Conditional" |

### Test infrastructure

- `mysql.connector` is stubbed with `MagicMock` before any project import
  so the suite runs with no MySQL installation.
- `_make_employee(**overrides)` and `_make_requirement(**overrides)` are
  shared fixture helpers that accept keyword overrides for targeted
  scenario construction.
- `_make_gap_analysis(employee, requirement)` reuses the actual Phase 2
  gap services to build a realistic gap dict — making the engine tests
  true integration tests without a database.

---

## 7. Output Format

### Phase 2 output (unchanged)
```json
{
  "employee": { ... },
  "gapAnalysis": {
    "skills": [ ... ],
    "certifications": [ ... ],
    "experience": { ... },
    "projects": { ... }
  }
}
```

### Phase 3 output (new)
```json
{
  "employee": {
    "employee_id": 1,
    "employee_code": "EMP001",
    "full_name": "Alice Smith",
    "department": "Engineering",
    "current_grade": "Grade B",
    "target_grade": "Grade A",
    "experience_years": 5.0,
    "performance_rating": 5.0
  },
  "readiness_score": 100.0,
  "readiness_level": "Promotion Ready",
  "promotion_decision": "Ready",
  "breakdown": {
    "skills": {
      "score": 40.0,
      "max_score": 40.0,
      "percentage": 100.0,
      "missing_skills": [],
      "weight": 40.0
    },
    "certifications": {
      "score": 15.0,
      "max_score": 15.0,
      "completed": 1,
      "missing": [],
      "weight": 15.0
    },
    "experience": {
      "score": 15.0,
      "current_years": 5.0,
      "required_years": 5.0,
      "gap_years": 0.0,
      "weight": 15.0
    },
    "projects": {
      "score": 20.0,
      "completed": 3,
      "required": 3,
      "remaining": 0,
      "lead_completed": 1,
      "lead_required": 1,
      "lead_remaining": 0,
      "weight": 20.0
    },
    "performance": {
      "score": 10.0,
      "performance_rating": 5.0,
      "weight": 10.0
    }
  }
}
```

---

## 8. How to Run

### Run the full pipeline
```bash
python main.py 1
```

### Run Phase 3 tests only
```bash
python -m unittest tests/test_readiness.py -v
```

### Run all tests (Phase 2 + Phase 3)
```bash
python -m unittest discover -s tests -v
```

---

## 9. What Phase 4 Will Build On

Phase 4 (Recommendations Engine) will receive the `ReadinessReport`
produced here and use the `breakdown` fields — specifically
`missing_skills`, `missing` certifications, `gap_years`, `remaining`
projects, and `performance_rating` — to generate targeted recommendations
for courses, mentors, certifications, and projects.

Phase 3 deliberately stops at scoring and decision-making. It does not
suggest any remediation actions.
