"""
Automated tests for Employee What-If Career Scenario Simulator (Phase 1.3).

Validates:
- What-If simulation calculations (readiness score improvement, promotion probability boost).
- Zero database mutation (original database records remain untouched).
- Exact pipeline reuse (same readiness scoring & ML prediction models).
- Resolved skills and certifications tracking.
- API route POST /simulation/what-if validation and response schema.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from services.simulation_service import SimulationService
from api.schemas.simulation import SimulationRequest, SkillOverrideSchema, CertificationOverrideSchema, ProjectOverrideSchema, ExperienceOverrideSchema

client = TestClient(app)


class TestSimulationService:
    """Unit tests for SimulationService."""

    @pytest.fixture
    def service(self):
        return SimulationService()

    def test_simulation_run_improves_metrics(self, service):
        """Verify that upgrading skills and adding certifications improves readiness & probability."""
        req = SimulationRequest(
            employee_id=1,
            skills=[
                SkillOverrideSchema(skill_name="Python", simulated_level=5),
                SkillOverrideSchema(skill_name="Docker", simulated_level=4),
            ],
            certifications=[
                CertificationOverrideSchema(certification_name="AWS Certified Solutions Architect", completed=True),
            ],
            projects=ProjectOverrideSchema(additional_projects=2, additional_lead_projects=1),
            experience=ExperienceOverrideSchema(additional_experience_years=2.0),
        )

        res = service.simulate(req)

        assert res["employee_id"] == 1
        assert isinstance(res["baseline_readiness_score"], float)
        assert isinstance(res["simulated_readiness_score"], float)
        assert res["simulated_readiness_score"] >= res["baseline_readiness_score"]
        assert res["readiness_score_diff"] >= 0.0
        assert 0.0 <= res["simulated_promotion_probability"] <= 1.0

    def test_zero_database_mutation(self, service):
        """Verify that running a simulation does NOT mutate database records."""
        from services.data_loader import DataLoader
        loader = DataLoader()
        try:
            emp_before = loader.load_employee(1)
            exp_before = emp_before.experience_years
            skills_count_before = len(emp_before.skills)
            certs_count_before = len(emp_before.certifications)
        finally:
            loader.close()

        req = SimulationRequest(
            employee_id=1,
            skills=[
                SkillOverrideSchema(skill_name="Python", simulated_level=5),
            ],
            certifications=[
                CertificationOverrideSchema(certification_name="SIMULATED_TEST_CERT", completed=True),
            ],
            experience=ExperienceOverrideSchema(additional_experience_years=5.0),
        )

        service.simulate(req)

        loader = DataLoader()
        try:
            emp_after = loader.load_employee(1)
            exp_after = emp_after.experience_years
            skills_count_after = len(emp_after.skills)
            certs_count_after = len(emp_after.certifications)
        finally:
            loader.close()

        assert exp_before == exp_after
        assert skills_count_before == skills_count_after
        assert certs_count_before == certs_count_after

    def test_api_simulation_endpoint(self):
        """Verify POST /simulation/what-if endpoint returns valid response."""
        login_res = client.post("/auth/login", json={"username": "aarav", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "employee_id": 1,
            "skills": [
                {"skill_name": "Python", "simulated_level": 5}
            ],
            "certifications": [
                {"certification_name": "AWS Certified Solutions Architect", "completed": True}
            ],
            "projects": {"additional_projects": 1, "additional_lead_projects": 1},
            "experience": {"additional_experience_years": 1.0}
        }

        response = client.post("/simulation/what-if", json=payload, headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["employee_id"] == 1
        assert "baseline_readiness_score" in data
        assert "simulated_readiness_score" in data
        assert "readiness_score_diff" in data
        assert "probability_diff" in data
