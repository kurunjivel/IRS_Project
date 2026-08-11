"""
Priority Service — IRS Phase 6.

Applies the hybrid ML + rule-based priority boosting logic across
all recommendation categories.

This is the Phase 6 "hybrid" layer:
  - Phase 2 (rule-based gap analysis) determines WHAT gaps exist.
  - Phase 3 (readiness score) determines HOW URGENT the overall situation is.
  - Phase 5 (ML prediction) provides a probability signal for LIKELIHOOD.
  - PriorityService combines these signals to re-rank and augment recommendations.

Priority adjustments
--------------------
If the ML promotion_probability is LOW (< 0.40):
  - All mandatory-gap recommendations are pinned to HIGH.
  - A global "urgent" flag is set in the report context.

If the readiness score is very low (< 40):
  - Fundamental items (experience, all mandatory certs/skills) → HIGH.

If both readiness score ≥ 75 and ML probability ≥ 0.65:
  - MEDIUM → LOW for non-mandatory items (employee is mostly ready).
"""

from __future__ import annotations

import logging

from services.recommendation.recommendation_item import Priority, RecommendationItem

logger = logging.getLogger(__name__)

# Thresholds
_LOW_PROBABILITY_THRESHOLD:  float = 0.40
_LOW_READINESS_THRESHOLD:    float = 40.0
_HIGH_READINESS_THRESHOLD:   float = 75.0
_HIGH_PROBABILITY_THRESHOLD: float = 0.65


class PriorityService:
    """
    Re-ranks and adjusts recommendation priorities using ML + readiness signals.

    Stateless — no mutable instance state.
    """

    def adjust(
        self,
        recommendations: list[RecommendationItem],
        readiness_score: float,
        promotion_probability: float,
    ) -> list[RecommendationItem]:
        """
        Apply hybrid priority adjustments to a combined recommendation list.

        Args:
            recommendations:      Flat list of all recommendations across all
                                  categories (learning, cert, project, mentor).
            readiness_score:      Phase 3 overall readiness score (0–100).
            promotion_probability: Phase 5 ML promotion probability (0.0–1.0).

        Returns:
            The same list with adjusted priorities, re-sorted HIGH → MEDIUM → LOW.
        """
        low_probability  = promotion_probability < _LOW_PROBABILITY_THRESHOLD
        low_readiness    = readiness_score < _LOW_READINESS_THRESHOLD
        mostly_ready     = (
            readiness_score >= _HIGH_READINESS_THRESHOLD
            and promotion_probability >= _HIGH_PROBABILITY_THRESHOLD
        )

        for rec in recommendations:
            # Ensure all mandatory-gap items are HIGH when ML probability is low
            if low_probability and rec.metadata.get("mandatory"):
                rec.priority = Priority.HIGH
                logger.debug(
                    "Priority boosted to HIGH (low ML probability=%.2f): %s",
                    promotion_probability, rec.title,
                )

            # Boost fundamental items when readiness is very low
            if low_readiness and rec.metadata.get("mandatory"):
                rec.priority = Priority.HIGH

            # Downgrade non-mandatory MEDIUM → LOW when employee is mostly ready
            if mostly_ready and rec.priority == Priority.MEDIUM:
                is_mandatory = rec.metadata.get("mandatory", False)
                if not is_mandatory:
                    rec.priority = Priority.LOW
                    logger.debug(
                        "Priority downgraded to LOW (mostly ready): %s", rec.title
                    )

        # Re-sort globally: HIGH → MEDIUM → LOW, then by type for stability
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        recommendations.sort(key=lambda r: (order[r.priority], r.type.value))

        logger.info(
            "PriorityService: adjusted %d recommendations "
            "(readiness=%.1f, probability=%.2f).",
            len(recommendations), readiness_score, promotion_probability,
        )
        return recommendations

    def get_urgency_label(
        self,
        readiness_score: float,
        promotion_probability: float,
    ) -> str:
        """
        Return a human-readable urgency label for the overall recommendation
        context, combining rule-based and ML signals.

        Args:
            readiness_score:       Phase 3 score (0–100).
            promotion_probability: Phase 5 ML probability (0–1).

        Returns:
            One of: 'Critical', 'High', 'Moderate', 'Low', 'Minimal'.
        """
        if readiness_score < 40 or promotion_probability < 0.30:
            return "Critical"
        if readiness_score < 60 or promotion_probability < 0.45:
            return "High"
        if readiness_score < 75 or promotion_probability < 0.60:
            return "Moderate"
        if readiness_score < 90 or promotion_probability < 0.75:
            return "Low"
        return "Minimal"
