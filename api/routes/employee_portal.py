"""
Employee Portal API routes — Authenticated Self-Service Endpoints.

All endpoints automatically resolve employee_id from the authenticated identity,
preventing cross-employee data access.
"""

import logging
from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_user, require_employee
from services.career_service import CareerService
from services.promotion_messaging_service import build_employee_promotion_status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/employee", tags=["Employee Portal"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get my employee profile",
    description="Retrieve profile details for the authenticated employee.",
)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    return service.get_employee(emp_id)


@router.get(
    "/me/career-analysis",
    status_code=status.HTTP_200_OK,
    summary="Get my comprehensive career analysis",
    description="Retrieve full career analysis including profile, gap analysis, readiness score, ML prediction, and recommendations.",
)
def get_my_career_analysis(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    return service.get_career_analysis(emp_id)


@router.get(
    "/me/readiness",
    status_code=status.HTTP_200_OK,
    summary="Get my readiness score",
)
def get_my_readiness(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    return service.get_readiness(emp_id)


@router.get(
    "/me/recommendations",
    status_code=status.HTTP_200_OK,
    summary="Get my personalized recommendations",
)
def get_my_recommendations(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    return service.get_recommendations(emp_id)


@router.get(
    "/me/gap-analysis",
    status_code=status.HTTP_200_OK,
    summary="Get my gap analysis",
)
def get_my_gap_analysis(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    return service.get_gap_analysis(emp_id)


@router.get(
    "/me/roadmap",
    status_code=status.HTTP_200_OK,
    summary="Get my career roadmap timeline",
)
def get_my_roadmap(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    recs = service.get_recommendations(emp_id)
    return {"timeline": recs.get("timeline", [])}


@router.get(
    "/me/progress",
    status_code=status.HTTP_200_OK,
    summary="Get my career progression tracking status",
)
def get_my_progress(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    readiness = service.get_readiness(emp_id)
    pred = service.get_prediction(emp_id)
    return {
        "readiness_score": readiness.get("readiness_score", 0.0),
        "readiness_level": readiness.get("readiness_level", "Under Evaluation"),
        "promotion_decision": readiness.get("promotion_decision", "Pending"),
        "promotion_probability": pred.get("promotion_probability", 0.0),
    }


@router.get(
    "/me/promotion-status",
    status_code=status.HTTP_200_OK,
    summary="Get my promotion status in FIRST PERSON messaging",
)
def get_my_promotion_status(current_user: dict = Depends(get_current_user)):
    user = require_employee(current_user)
    emp_id = user["employee_id"]
    service = CareerService()
    analysis = service.get_career_analysis(emp_id)
    return build_employee_promotion_status(analysis)
