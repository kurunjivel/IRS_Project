"""
API Test & Audit Runner for Employee (aarav) and HR (hr).
Executes all API endpoints and records full details for reporting.
"""

import json
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def run_audit():
    report_data = {
        "employee_aarav": [],
        "hr_admin": [],
        "rbac_checks": []
    }

    # 1. Health check
    res = client.get("/health")
    report_data["health"] = {
        "status_code": res.status_code,
        "response": res.json()
    }

    # 2. Login Aarav (EMPLOYEE)
    res_aarav = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
    aarav_token = res_aarav.json().get("access_token")
    aarav_headers = {"Authorization": f"Bearer {aarav_token}"}
    report_data["employee_aarav"].append({
        "endpoint": "POST /auth/login",
        "status_code": res_aarav.status_code,
        "description": "Employee Login (aarav)",
        "response": res_aarav.json()
    })

    # 3. Login HR Admin (hr)
    res_hr = client.post("/auth/login", json={"username": "hr", "password": "password123"})
    hr_token = res_hr.json().get("access_token")
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    report_data["hr_admin"].append({
        "endpoint": "POST /auth/login",
        "status_code": res_hr.status_code,
        "description": "HR Administrator Login (hr)",
        "response": res_hr.json()
    })

    # Aarav (Employee) Endpoints
    aarav_endpoints = [
        ("GET /auth/me", "/auth/me", aarav_headers, "Get authenticated current user session info"),
        ("GET /employee/me", "/employee/me", aarav_headers, "Employee Self-Service Profile"),
        ("GET /employee/me/career-analysis", "/employee/me/career-analysis", aarav_headers, "Employee Self-Service Full Career Analysis Report"),
        ("GET /employee/me/roadmap", "/employee/me/roadmap", aarav_headers, "Employee Self-Service Milestone Timeline Roadmap"),
        ("GET /employee/me/progress", "/employee/me/progress", aarav_headers, "Employee Self-Service Readiness Score & ML Prediction Progress"),
        ("GET /employee/1", "/employee/1", aarav_headers, "Get Employee Profile by ID (1)"),
        ("GET /gap-analysis/1", "/gap-analysis/1", aarav_headers, "Get Phase 2 Gap Analysis Report for Employee ID 1"),
        ("GET /readiness/1", "/readiness/1", aarav_headers, "Get Phase 3 Readiness Score for Employee ID 1"),
        ("GET /prediction/1", "/prediction/1", aarav_headers, "Get Phase 5 ML Promotion Prediction for Employee ID 1"),
        ("GET /recommendations/1", "/recommendations/1", aarav_headers, "Get Phase 6 Hybrid Recommendations for Employee ID 1"),
        ("GET /career-analysis/1", "/career-analysis/1", aarav_headers, "Get Phase 7 Consolidated Career Analysis Report for Employee ID 1"),
    ]

    for label, path, headers, desc in aarav_endpoints:
        r = client.get(path, headers=headers)
        report_data["employee_aarav"].append({
            "endpoint": label,
            "status_code": r.status_code,
            "description": desc,
            "response": r.json()
        })

    # HR Endpoints for HR Admin (hr)
    hr_endpoints = [
        ("GET /auth/me", "/auth/me", hr_headers, "Get authenticated HR user session info"),
        ("GET /hr/employees", "/hr/employees", hr_headers, "List all active employees in organization"),
        ("GET /hr/roles", "/hr/roles", hr_headers, "List available target roles/grades"),
        ("GET /hr/roles/3/candidates", "/hr/roles/3/candidates", hr_headers, "Rank candidate employees for Target Role G3"),
        ("GET /hr/employees/1/career-analysis", "/hr/employees/1/career-analysis", hr_headers, "Detailed employee career analysis with HR third-person messaging for Employee ID 1"),
        ("GET /hr/employees/1/promotion-status", "/hr/employees/1/promotion-status", hr_headers, "HR Third-Person Promotion Assessment for Employee ID 1"),
        ("GET /hr/analytics", "/hr/analytics", hr_headers, "HR Talent Pipeline Workforce Analytics"),
        ("GET /employee/1", "/employee/1", hr_headers, "HR View Employee Profile by ID 1"),
        ("GET /career-analysis/1", "/career-analysis/1", hr_headers, "HR View Consolidated Career Analysis Report for Employee ID 1"),
    ]

    for label, path, headers, desc in hr_endpoints:
        r = client.get(path, headers=headers)
        report_data["hr_admin"].append({
            "endpoint": label,
            "status_code": r.status_code,
            "description": desc,
            "response": r.json()
        })

    # RBAC Enforcement Checks
    # Employee attempting HR endpoints -> Expect 403 Forbidden
    rbac_tests = [
        ("Employee 'aarav' accessing HR Employee List (/hr/employees)", "/hr/employees", aarav_headers, 403),
        ("Employee 'aarav' accessing HR Roles List (/hr/roles)", "/hr/roles", aarav_headers, 403),
        ("Employee 'aarav' accessing HR Candidate Ranking (/hr/roles/3/candidates)", "/hr/roles/3/candidates", aarav_headers, 403),
        ("Employee 'aarav' accessing HR Candidate Career Analysis (/hr/employees/1/career-analysis)", "/hr/employees/1/career-analysis", aarav_headers, 403),
        ("Employee 'aarav' accessing HR Candidate Promotion Status (/hr/employees/1/promotion-status)", "/hr/employees/1/promotion-status", aarav_headers, 403),
        ("Employee 'aarav' accessing HR Analytics (/hr/analytics)", "/hr/analytics", aarav_headers, 403),
        ("Unauthenticated user accessing protected endpoint (/employee/me)", "/employee/me", {}, 401),
        ("Unauthenticated user accessing HR Analytics (/hr/analytics)", "/hr/analytics", {}, 401),
    ]

    for label, path, headers, expected_status in rbac_tests:
        r = client.get(path, headers=headers)
        report_data["rbac_checks"].append({
            "test": label,
            "expected_status": expected_status,
            "actual_status": r.status_code,
            "status_matched": (r.status_code == expected_status),
            "response": r.json()
        })

    with open("scratch/api_audit_results.json", "w") as f:
        json.dump(report_data, f, indent=2)

    print("Audit complete! Saved to scratch/api_audit_results.json")

if __name__ == "__main__":
    run_audit()
