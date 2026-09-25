"""
Manager Review and Calibration Domain Models — Phase 1 Enhancement 4.

Models for quarterly manager evaluations, competency ratings,
approval workflow status, and audit history.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class ReviewStatus:
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_DEVELOPMENT = "NEEDS_DEVELOPMENT"

    ALL_STATUSES = {PENDING, IN_REVIEW, APPROVED, REJECTED, NEEDS_DEVELOPMENT}


@dataclass
class ManagerReview:
    """Quarterly manager review and calibration assessment."""

    review_id: Optional[int]
    employee_id: int
    manager_id: int
    quarter: str
    status: str = ReviewStatus.PENDING
    technical_competency: int = 3
    communication: int = 3
    leadership: int = 3
    teamwork: int = 3
    ownership: int = 3
    overall_assessment: Optional[str] = None
    comments: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def validate(self) -> list[str]:
        """Validate ratings and comments requirement."""
        errors = []
        if self.status not in ReviewStatus.ALL_STATUSES:
            errors.append(f"Invalid review status '{self.status}'. Must be one of {ReviewStatus.ALL_STATUSES}")

        for attr, label in [
            (self.technical_competency, "Technical Competency"),
            (self.communication, "Communication"),
            (self.leadership, "Leadership"),
            (self.teamwork, "Teamwork"),
            (self.ownership, "Ownership"),
        ]:
            if not (1 <= attr <= 5):
                errors.append(f"{label} score must be between 1 and 5 (got {attr})")

        if self.status in (ReviewStatus.REJECTED, ReviewStatus.NEEDS_DEVELOPMENT):
            if not self.comments or not self.comments.strip():
                errors.append(f"Comments are mandatory when status is {self.status}")

        return errors


@dataclass
class ReviewAuditLog:
    """Audit log entry tracking status transitions and feedback history."""

    audit_id: Optional[int]
    review_id: int
    employee_id: int
    manager_id: int
    previous_status: Optional[str]
    new_status: str
    comments: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
