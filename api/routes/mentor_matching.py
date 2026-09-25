"""
Phase 8 — Automated Peer & Mentor Matching Network API Routes.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Path, Query, status, HTTPException
from pydantic import BaseModel, Field

from services.career_service import CareerService
from services.gap_analysis_service import EmployeeNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mentors", tags=["Mentor Matching"])


class MentorshipRequestInput(BaseModel):
    employee_id: int = Field(..., ge=1, description="ID of employee requesting mentorship")
    mentor_id: int = Field(..., ge=1, description="ID of candidate mentor selected")
    skill_gap_focus: Optional[str] = Field(None, description="Optional primary skill focus for mentorship")
    notes: Optional[str] = Field(None, description="Optional message to mentor")


@router.get(
    "/matches/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Get automated peer & mentor matches",
    description="Retrieve ranked mentor and peer learning partner recommendations based on Phase 8 multi-factor evaluation.",
)
def get_mentor_matches(
    employee_id: int = Path(..., ge=1, description="Unique positive integer employee ID"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of matches to return"),
):
    """Retrieve ranked mentor/peer matches for an employee."""
    logger.info("API GET /mentors/matches/%s requested (limit=%s)", employee_id, limit)
    service = CareerService()
    try:
        return service.get_mentor_matches(employee_id, limit=limit)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("Error generating mentor matches for %s: %s", employee_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/request",
    status_code=status.HTTP_201_CREATED,
    summary="Submit a mentorship connection request",
    description="Request a mentorship connection with a matched mentor or peer learning partner.",
)
def request_mentorship(input_data: MentorshipRequestInput):
    """Submit a mentorship connection request."""
    logger.info(
        "API POST /mentors/request: employee %s requested mentor %s",
        input_data.employee_id, input_data.mentor_id
    )
    # Return connection confirmation record
    return {
        "status": "SUCCESS",
        "message": f"Mentorship connection request successfully sent to mentor ID {input_data.mentor_id}.",
        "request_details": {
            "employee_id": input_data.employee_id,
            "mentor_id": input_data.mentor_id,
            "skill_gap_focus": input_data.skill_gap_focus,
            "notes": input_data.notes,
            "connection_status": "PENDING_ACCEPTANCE",
        },
    }
