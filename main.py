"""
IRS — Gap Analysis (Phase 2) + Readiness Scoring (Phase 3) entry point.

Usage:
    python main.py <employee_id>
    python main.py          # defaults to employee_id = 1
"""

import json
import logging
import sys

from services.gap_analysis_service import (
    GapAnalysisService,
    EmployeeNotFoundError,
    GradeNotFoundError,
)
from services.json_builder import JsonBuilder
from services.readiness.readiness_engine import ReadinessEngine
from services.readiness.readiness_report import ReadinessReportBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Run the full IRS pipeline for a given employee ID.

    Phase 2: Gap Analysis
    Phase 3: Readiness Scoring
    """
    employee_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    gap_service = GapAnalysisService()
    json_builder = JsonBuilder()
    readiness_engine = ReadinessEngine()
    report_builder = ReadinessReportBuilder()

    try:
        # ── Phase 2: Gap Analysis ──────────────────────────────────────────
        logger.info("Phase 2 — Gap analysis for employee_id=%s", employee_id)
        gap_analysis = gap_service.run(employee_id)

        gap_report = json_builder.build(gap_analysis)
        print("\n=== Phase 2 — Gap Analysis Report ===")
        print(json.dumps(gap_report, indent=2, default=str))

        # ── Phase 3: Readiness Scoring ─────────────────────────────────────
        logger.info("Phase 3 — Readiness scoring for employee_id=%s", employee_id)
        readiness_result = readiness_engine.calculate(gap_analysis)

        readiness_report = report_builder.build(gap_analysis["employee"], readiness_result)

        print("\n=== Phase 3 — Promotion Readiness Report ===")
        print(json.dumps(readiness_report.__dict__, indent=2, default=str))

    except EmployeeNotFoundError as exc:
        logger.error(exc)
        sys.exit(1)
    except GradeNotFoundError as exc:
        logger.error(exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        sys.exit(1)
    finally:
        gap_service.close()


if __name__ == "__main__":
    main()
