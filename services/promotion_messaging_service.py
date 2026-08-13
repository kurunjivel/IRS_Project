"""
Promotion Messaging Service — Shared presentation logic for Employee and HR views.

Consumes standard IRS engine career analysis outputs and formats promotion status
and gap explanations into first-person (Employee) or third-person (HR) messaging.
"""

import logging

logger = logging.getLogger(__name__)


def build_employee_promotion_status(career_analysis: dict) -> dict:
    """
    Format promotion analysis into FIRST PERSON messaging for Employee portal.
    """
    emp = career_analysis.get("employee", {})
    readiness = career_analysis.get("readiness", {})
    prediction = career_analysis.get("prediction", {})
    gap_analysis = career_analysis.get("gap_analysis", {})

    target_grade = emp.get("target_grade", "G3")
    full_name = emp.get("full_name", "Employee")
    readiness_score = readiness.get("readiness_score", 0.0)
    prob = prediction.get("promotion_probability", 0.0) * 100.0

    skill_gaps = gap_analysis.get("skills", [])
    cert_gaps = gap_analysis.get("certifications", [])
    exp_gap = gap_analysis.get("experience", {})
    proj_gap = gap_analysis.get("projects", {})

    missing_items = []
    for s in skill_gaps:
        if s.get("gap", 0) > 0:
            missing_items.append({
                "title": f"{s.get('skill', 'Skill')} proficiency",
                "current": s.get("current_level", 0),
                "required": s.get("required_level", 0),
                "detail": f"Current: {s.get('current_level', 0)}, Required: {s.get('required_level', 0)}"
            })

    for c in cert_gaps:
        cert_name = c.get("certification") or c.get("certification_name") or "Certification"
        missing_items.append({
            "title": cert_name,
            "status": "Not completed",
            "detail": "Status: Not completed"
        })

    if exp_gap.get("remaining_years", 0) > 0:
        missing_items.append({
            "title": "Experience",
            "detail": f"Current: {exp_gap.get('current_years', 0)} yrs, Required: {exp_gap.get('required_years', 0)} yrs"
        })

    if proj_gap.get("remaining_projects", 0) > 0:
        missing_items.append({
            "title": "Project Portfolio",
            "detail": f"Current: {proj_gap.get('total_projects', 0)}, Required: {proj_gap.get('required_projects', 0)}"
        })

    is_eligible = readiness_score >= 85.0 and len(missing_items) == 0

    if is_eligible:
        header_message = f"You are eligible for promotion to {target_grade}."
    else:
        header_message = f"You are not currently eligible for promotion to {target_grade}."

    return {
        "perspective": "FIRST_PERSON",
        "employee_id": emp.get("employee_id"),
        "full_name": full_name,
        "current_grade": emp.get("current_grade"),
        "target_grade": target_grade,
        "is_eligible": is_eligible,
        "eligibility_text": "Eligible" if is_eligible else "Not Eligible",
        "status_title": "YOUR PROMOTION STATUS",
        "headline": header_message,
        "readiness_score": readiness_score,
        "readiness_text": f"{readiness_score:.2f} / 100",
        "promotion_probability": round(prob, 1),
        "promotion_probability_text": f"{prob:.1f}%",
        "gap_headline": "Why are you not ready?" if not is_eligible else "All requirements satisfied!",
        "gaps": missing_items,
        "recommended_action": "Complete the identified career-development activities." if not is_eligible else "Submit your promotion application to HR."
    }


def build_hr_promotion_status(career_analysis: dict) -> dict:
    """
    Format promotion analysis into THIRD PERSON messaging for HR dashboard.
    """
    emp = career_analysis.get("employee", {})
    readiness = career_analysis.get("readiness", {})
    prediction = career_analysis.get("prediction", {})
    gap_analysis = career_analysis.get("gap_analysis", {})

    full_name = emp.get("full_name", "Employee")
    target_grade = emp.get("target_grade", "G3")
    readiness_score = readiness.get("readiness_score", 0.0)
    prob = prediction.get("promotion_probability", 0.0) * 100.0

    skill_gaps = gap_analysis.get("skills", [])
    cert_gaps = gap_analysis.get("certifications", [])
    exp_gap = gap_analysis.get("experience", {})
    proj_gap = gap_analysis.get("projects", {})

    reasons = []
    for s in skill_gaps:
        if s.get("gap", 0) > 0:
            reasons.append(f"{s.get('skill', 'Skill')} proficiency gap")

    for c in cert_gaps:
        cert_name = c.get("certification") or c.get("certification_name") or "Certification"
        reasons.append(f"{cert_name} certification missing")

    if exp_gap.get("remaining_years", 0) > 0:
        reasons.append(f"{exp_gap.get('remaining_years', 0)} years of experience still required")

    if proj_gap.get("remaining_projects", 0) > 0:
        reasons.append(f"{proj_gap.get('remaining_projects', 0)} project(s) still required")

    is_eligible = readiness_score >= 85.0 and len(reasons) == 0

    if is_eligible:
        headline = f"{full_name} is eligible for promotion to {target_grade}."
    else:
        headline = f"{full_name} is not currently eligible for promotion to {target_grade}."

    return {
        "perspective": "THIRD_PERSON",
        "employee_id": emp.get("employee_id"),
        "full_name": full_name,
        "current_grade": emp.get("current_grade"),
        "target_grade": target_grade,
        "is_eligible": is_eligible,
        "eligibility_text": "Eligible" if is_eligible else "Not Eligible",
        "status_title": "PROMOTION ELIGIBILITY",
        "headline": headline,
        "readiness_score": readiness_score,
        "readiness_text": f"{readiness_score:.2f} / 100",
        "promotion_probability": round(prob, 1),
        "promotion_probability_text": f"{prob:.1f}%",
        "gap_headline": "Reason:" if not is_eligible else "All mandatory requirements have been satisfied.",
        "reasons": reasons,
        "recommended_action": "Complete the identified career-development activities." if not is_eligible else "Approve promotion workflow."
    }
