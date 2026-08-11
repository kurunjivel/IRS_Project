"""
Recommendation data models — IRS Phase 6.

Shared dataclasses and enumerations used across all recommendation services.
These are pure data containers with no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Priority levels
# ---------------------------------------------------------------------------

class Priority(str, Enum):
    """Priority level for a recommendation."""
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


# ---------------------------------------------------------------------------
# Recommendation types
# ---------------------------------------------------------------------------

class RecommendationType(str, Enum):
    """Category of recommendation produced by the engine."""
    LEARNING      = "Learning"
    CERTIFICATION = "Certification"
    PROJECT       = "Project"
    MENTORSHIP    = "Mentorship"


# ---------------------------------------------------------------------------
# Core recommendation item
# ---------------------------------------------------------------------------

@dataclass
class RecommendationItem:
    """
    A single actionable recommendation for an employee.

    Attributes:
        type:            Category (Learning / Certification / Project / Mentorship).
        title:           Short descriptive title for the recommendation.
        reason:          Explanation of why this is recommended.
        priority:        HIGH / MEDIUM / LOW.
        provider:        Source or provider (course provider, mentor name, etc.).
        duration:        Expected time investment (e.g. '3 months', '40 hours').
        impact:          Expected impact on the readiness score / promotion chance.
        metadata:        Optional extra data (course_id, cert_name, etc.).
    """

    type:     RecommendationType
    title:    str
    reason:   str
    priority: Priority
    provider: str          = ""
    duration: str          = ""
    impact:   str          = ""
    metadata: dict         = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dict representation."""
        return {
            "type":     self.type.value,
            "title":    self.title,
            "reason":   self.reason,
            "priority": self.priority.value,
            "provider": self.provider,
            "duration": self.duration,
            "impact":   self.impact,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Timeline milestone
# ---------------------------------------------------------------------------

@dataclass
class TimelineMilestone:
    """A single milestone in the career progression timeline."""

    month:       int     # Estimated month from now (1-indexed)
    title:       str     # Short milestone title
    description: str     # What should be achieved by this milestone
    category:    str     # Learning / Certification / Project / Readiness

    def to_dict(self) -> dict:
        return {
            "month":       self.month,
            "title":       self.title,
            "description": self.description,
            "category":    self.category,
        }
