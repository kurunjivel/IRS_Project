"""
Certification Recommendation Service — IRS Phase 6.

Maps certification gaps (from Phase 2) to actionable certification
recommendations, enriched with provider details from the database.

Priority rules
--------------
- Mandatory certification gap → HIGH
- Non-mandatory gap           → MEDIUM
"""

from __future__ import annotations

import logging

from services.recommendation.recommendation_item import (
    Priority,
    RecommendationItem,
    RecommendationType,
)

logger = logging.getLogger(__name__)


class CertificationService:
    """
    Generates certification recommendations from certification gaps.

    Stateless — no mutable instance state.
    """

    def recommend(
        self,
        certification_gaps: list[dict],
        cert_details: list[dict],
    ) -> list[RecommendationItem]:
        """
        Build certification recommendations from gaps.

        Args:
            certification_gaps: The list returned by CertificationGapService.analyze().
                                Each dict has: certification, provider, mandatory.
            cert_details:       Certification details rows from the repository
                                (grade_certification_requirements JOIN certifications).
                                Each dict has: certification_name, provider, mandatory.

        Returns:
            Ordered list of RecommendationItems (HIGH first).
        """
        # Build a details lookup for quick access
        details_map: dict[str, dict] = {
            row["certification_name"].lower(): row
            for row in cert_details
        }

        recommendations: list[RecommendationItem] = []

        for gap in certification_gaps:
            cert_name: str = gap["certification"]
            provider: str  = gap.get("provider", "")
            mandatory: bool = gap["mandatory"]
            priority = Priority.HIGH if mandatory else Priority.MEDIUM

            # Enrich with DB details if available
            detail = details_map.get(cert_name.lower(), {})
            enriched_provider = detail.get("provider") or provider

            reason = (
                f"You have not completed the '{cert_name}' certification, "
                f"which is a "
                f"{'mandatory' if mandatory else 'recommended'} "
                f"requirement for the target grade."
            )
            impact = (
                "Mandatory requirement — must be completed before promotion can proceed"
                if mandatory
                else "Improves certification readiness score"
            )

            recommendations.append(RecommendationItem(
                type=RecommendationType.CERTIFICATION,
                title=f"Obtain certification: {cert_name}",
                reason=reason,
                priority=priority,
                provider=enriched_provider,
                duration="",          # cert preparation time varies
                impact=impact,
                metadata={
                    "certification_name": cert_name,
                    "provider":           enriched_provider,
                    "mandatory":          mandatory,
                },
            ))

        # Sort: HIGH first
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        recommendations.sort(key=lambda r: order[r.priority])

        logger.info(
            "CertificationService: %d recommendation(s) generated "
            "(cert_gaps=%d).",
            len(recommendations), len(certification_gaps),
        )
        return recommendations
