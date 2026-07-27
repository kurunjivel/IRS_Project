"""
IRS Phase 2 — Gap Analysis Engine entry point.

Usage:
    python main.py <employee_id>
    python main.py          # defaults to employee_id = 1
"""

import json
import logging
import sys

from services.gap_analysis_service import GapAnalysisService, EmployeeNotFoundError, GradeNotFoundError
from services.json_builder import JsonBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Run the gap analysis pipeline for a given employee ID.

    Reads the employee ID from the command line (defaults to 1),
    runs the full gap analysis, and prints the JSON report.
    """
    employee_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    service = GapAnalysisService()
    builder = JsonBuilder()

    try:
        logger.info("Starting gap analysis for employee_id=%s", employee_id)
        analysis = service.run(employee_id)
        report = builder.build(analysis)
        print(json.dumps(report, indent=2, default=str))
    except EmployeeNotFoundError as e:
        logger.error(e)
        sys.exit(1)
    except GradeNotFoundError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        sys.exit(1)
    finally:
        service.close()


if __name__ == "__main__":
    main()
