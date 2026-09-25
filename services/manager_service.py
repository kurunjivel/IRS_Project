"""
Manager Service — Phase 1 Enhancement 4.

Business logic service for manager evaluation, direct report access authorization,
quarterly calibration, review approvals, and audit trail generation.
"""

import logging
from typing import Optional
from fastapi import HTTPException, status

from database.manager_repository import ManagerRepository
from database.user_repository import UserRepository
from models.manager_review import ManagerReview, ReviewAuditLog, ReviewStatus
from services.career_service import CareerService

logger = logging.getLogger(__name__)


class ManagerService:
    """Service handling manager review workflows, calibration, and direct report authorization."""

    def __init__(self, manager_repo: Optional[ManagerRepository] = None, career_svc: Optional[CareerService] = None) -> None:
        self._manager_repo = manager_repo or ManagerRepository()
        self._career_svc = career_svc or CareerService()

    def close(self) -> None:
        if hasattr(self._manager_repo, "close"):
            self._manager_repo.close()

    def verify_direct_report(self, manager_id: int, employee_id: int) -> None:
        """
        Verify that manager_id is authorized to view or manage employee_id.

        Raises:
            HTTPException(403): If the employee is not assigned to this manager.
        """
        if not self._manager_repo.is_manager_of(manager_id, employee_id):
            logger.warning("Manager %s attempted unauthorized access to employee %s", manager_id, employee_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You can only access direct reports assigned to you.",
            )

    def get_team_members(self, manager_id: int) -> list[dict]:
        """Fetch list of direct reports assigned to manager with baseline readiness & review status."""
        emp_ids = self._manager_repo.get_managed_employee_ids(manager_id)
        team = []
        for emp_id in emp_ids:
            try:
                career_data = self._career_svc.get_career_analysis(emp_id)
                emp = career_data.get("employee", {})
                readiness = career_data.get("readiness", {})
                prediction = career_data.get("prediction", {})

                review = self._manager_repo.get_review(emp_id, quarter="Q3-2026")
                review_status = review["status"] if review else ReviewStatus.PENDING

                team.append({
                    "employee_id": emp_id,
                    "full_name": emp.get("full_name", f"Employee #{emp_id}"),
                    "email": emp.get("email", ""),
                    "department": emp.get("department", ""),
                    "current_grade": emp.get("current_grade", ""),
                    "target_grade": emp.get("target_grade", ""),
                    "readiness_score": readiness.get("readiness_score", 0.0),
                    "promotion_probability": prediction.get("promotion_probability", 0.0),
                    "review_status": review_status,
                    "review_details": review,
                })
            except Exception as e:
                logger.error("Failed to load direct report data for employee %s: %s", emp_id, e)

        return team

    def get_employee_dossier(self, manager_id: int, employee_id: int) -> dict:
        """
        Get full evaluation dossier for direct report.
        Requires direct report authorization check.
        """
        self.verify_direct_report(manager_id, employee_id)

        analysis = self._career_svc.get_career_analysis(employee_id)
        review = self._manager_repo.get_review(employee_id, quarter="Q3-2026")
        audits = self._manager_repo.get_audit_history(employee_id)

        return {
            "career_analysis": analysis,
            "current_review": review or {
                "employee_id": employee_id,
                "manager_id": manager_id,
                "quarter": "Q3-2026",
                "status": ReviewStatus.PENDING,
                "technical_competency": 3,
                "communication": 3,
                "leadership": 3,
                "teamwork": 3,
                "ownership": 3,
                "overall_assessment": "",
                "comments": "",
            },
            "audit_history": audits,
        }

    def submit_review(
        self,
        manager_id: int,
        employee_id: int,
        quarter: str,
        review_status: str,
        technical_competency: int,
        communication: int,
        leadership: int,
        teamwork: int,
        ownership: int,
        overall_assessment: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> dict:
        """
        Submit or update quarterly manager calibration and review decision.

        Enforces comment validation on REJECTED or NEEDS_DEVELOPMENT.
        Logs an entry in the audit trail.
        """
        self.verify_direct_report(manager_id, employee_id)

        review = ManagerReview(
            review_id=None,
            employee_id=employee_id,
            manager_id=manager_id,
            quarter=quarter or "Q3-2026",
            status=review_status,
            technical_competency=technical_competency,
            communication=communication,
            leadership=leadership,
            teamwork=teamwork,
            ownership=ownership,
            overall_assessment=overall_assessment,
            comments=comments,
        )

        validation_errors = review.validate()
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {'; '.join(validation_errors)}",
            )

        existing_review = self._manager_repo.get_review(employee_id, quarter=review.quarter)
        previous_status = existing_review["status"] if existing_review else None

        saved_review = self._manager_repo.save_review(review)

        # Log audit entry
        audit = ReviewAuditLog(
            audit_id=None,
            review_id=saved_review["review_id"],
            employee_id=employee_id,
            manager_id=manager_id,
            previous_status=previous_status,
            new_status=review.status,
            comments=comments or overall_assessment or "Review submitted",
        )
        saved_audit = self._manager_repo.log_audit(audit)

        return {
            "message": f"Manager review successfully updated to '{review.status}'.",
            "review": saved_review,
            "audit": saved_audit,
        }

    def get_audit_history(self, manager_id: int, employee_id: int) -> list[dict]:
        """Fetch audit log history for a direct report."""
        self.verify_direct_report(manager_id, employee_id)
        return self._manager_repo.get_audit_history(employee_id)
