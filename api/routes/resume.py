"""
API Routes for Resume/CV Parsing and Profile Confirmation.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_current_user, require_employee
from services.resume.text_extractor import TextExtractor, UnextractableTextError
from services.resume.resume_parser_service import ResumeParserService
from services.resume.profile_update_service import ProfileUpdateService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Resume Parser"])


class ConfirmProfileChangesPayload(BaseModel):
    confirmed_skills: List[Dict[str, Any]] = Field(default_factory=list)
    confirmed_certifications: List[Dict[str, Any]] = Field(default_factory=list)
    confirmed_projects: List[Dict[str, Any]] = Field(default_factory=list)


@router.post(
    "/employee/me/resume/parse",
    status_code=status.HTTP_200_OK,
    summary="Upload & Parse Resume/CV",
    description="Upload a PDF, DOCX, or TXT resume to extract structured career data and generate candidate profile updates for review.",
)
async def parse_my_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload resume file and return candidate profile updates diff for employee review."""
    user = require_employee(current_user)
    emp_id = user["employee_id"]

    logger.info("API POST /employee/me/resume/parse received filename='%s' from emp_id=%s", file.filename, emp_id)

    try:
        content = await file.read()
        extracted_text = TextExtractor.extract_text(content, file.filename)
        
        parser_svc = ResumeParserService()
        result = parser_svc.parse_resume_text(extracted_text, file.filename, emp_id)

        return result.to_dict()
    except UnextractableTextError as e:
        logger.warning("Unextractable text from file '%s': %s", file.filename, e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ValueError as e:
        logger.warning("Resume validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Error parsing resume for emp_id=%s: %s", emp_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/employee/me/resume/confirm",
    status_code=status.HTTP_200_OK,
    summary="Confirm & Apply Profile Updates",
    description="Confirm reviewed candidate changes from resume parsing to explicitly update employee profile records in the database.",
)
def confirm_my_profile_changes(
    payload: ConfirmProfileChangesPayload,
    current_user: dict = Depends(get_current_user),
):
    """Apply employee-confirmed resume updates to the database."""
    user = require_employee(current_user)
    emp_id = user["employee_id"]

    logger.info("API POST /employee/me/resume/confirm for emp_id=%s", emp_id)

    try:
        update_svc = ProfileUpdateService()
        res = update_svc.confirm_and_apply_updates(
            employee_id=emp_id,
            confirmed_skills=payload.confirmed_skills,
            confirmed_certifications=payload.confirmed_certifications,
            confirmed_projects=payload.confirmed_projects,
        )
        return res
    except Exception as e:
        logger.error("Error updating profile for emp_id=%s: %s", emp_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
