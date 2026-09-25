"""
Unit and integration tests for Resume/CV Parser and Intelligent Profile Extraction.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from services.resume.text_extractor import TextExtractor, UnextractableTextError
from services.resume.resume_parser_service import ResumeParserService
from services.resume.profile_update_service import ProfileUpdateService
from api.main import app


class TestTextExtractor:

    def test_extract_txt(self):
        text_bytes = b"Skills: Python, FastAPI, Docker\nExperience: 5 years software engineer."
        extracted = TextExtractor.extract_text(text_bytes, "resume.txt")
        assert "Python" in extracted
        assert "FastAPI" in extracted

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported file format"):
            TextExtractor.extract_text(b"data", "resume.xyz")

    def test_empty_txt_raises_unextractable(self):
        with pytest.raises(UnextractableTextError):
            TextExtractor.extract_text(b"  ", "empty.txt")


class TestResumeParserService:

    @patch("services.resume.resume_parser_service.EmployeeRepository")
    def test_parse_resume_text_and_compare(self, mock_emp_repo_cls):
        mock_emp_repo = MagicMock()
        mock_emp_repo.get_employee.return_value = {"employee_id": 1, "full_name": "John Doe"}
        mock_emp_repo.get_employee_skills.return_value = [
            {"skill_name": "Python", "skill_level": 3, "category": "Backend"},
        ]
        mock_emp_repo.get_employee_certifications.return_value = []
        mock_emp_repo.get_employee_projects.return_value = []
        mock_emp_repo_cls.return_value = mock_emp_repo

        resume_text = """
        John Doe Resume
        Technical Skills: Senior Python developer, FastAPI, Docker, Kubernetes, AWS.
        Certifications: AWS Certified Solutions Architect
        Projects: Microservices Migration project lead.
        """

        service = ResumeParserService(emp_repo=mock_emp_repo)
        result = service.parse_resume_text(resume_text, "john_resume.txt", employee_id=1)

        changes = result.candidate_changes
        assert changes["total_candidate_updates"] > 0
        
        # Check new skills (Docker, Kubernetes, AWS, FastAPI)
        new_sk_names = [s["skill_name"] for s in changes["new_skills"]]
        assert "Docker" in new_sk_names or "Kubernetes" in new_sk_names

        # Check upgraded skills (Python level upgraded from 3 to 4 due to "Senior Python")
        upg_sk_names = [s["skill_name"] for s in changes["upgraded_skills"]]
        assert "Python" in upg_sk_names

        # Check certifications
        assert len(changes["new_certifications"]) == 1
        assert changes["new_certifications"][0]["certification_name"] == "AWS Certified Solutions Architect"


class TestProfileUpdateService:

    @patch("services.resume.profile_update_service.EmployeeRepository")
    def test_confirm_and_apply_updates(self, mock_emp_repo_cls):
        mock_emp_repo = MagicMock()
        mock_emp_repo.update_employee_profile_data.return_value = True
        mock_emp_repo.get_employee_skills.return_value = [
            {"skill_name": "Python", "skill_level": 4},
            {"skill_name": "Kubernetes", "skill_level": 3},
        ]
        mock_emp_repo.get_employee_certifications.return_value = [{"certification_name": "AWS Certified Developer"}]
        mock_emp_repo.get_employee_projects.return_value = [{"project_name": "Cloud Migration"}]
        mock_emp_repo_cls.return_value = mock_emp_repo

        svc = ProfileUpdateService(emp_repo=mock_emp_repo)
        res = svc.confirm_and_apply_updates(
            employee_id=1,
            confirmed_skills=[{"skill_name": "Kubernetes", "suggested_level": 3}],
            confirmed_certifications=[{"certification_name": "AWS Certified Developer"}],
            confirmed_projects=[{"project_name": "Cloud Migration"}],
        )

        assert res["status"] == "SUCCESS"
        assert res["applied_updates"]["skills_added_or_upgraded"] == 1
        assert res["applied_updates"]["certifications_added"] == 1


class TestResumeAPI:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch("api.routes.resume.ResumeParserService")
    def test_parse_resume_api(self, mock_parser_svc_cls, client):
        from api.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {
            "username": "employee1", "role": "EMPLOYEE", "employee_id": 1
        }
        try:
            mock_svc = MagicMock()
            mock_svc.parse_resume_text.return_value = MagicMock(
                to_dict=lambda: {
                    "filename": "test.txt",
                    "extracted_sections": ["Skills"],
                    "candidate_changes": {"new_skills": [], "upgraded_skills": [], "total_candidate_updates": 0},
                    "raw_preview": "preview text",
                }
            )
            mock_parser_svc_cls.return_value = mock_svc

            files = {"file": ("resume.txt", b"Skills: Python, FastAPI", "text/plain")}
            response = client.post("/employee/me/resume/parse", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == "test.txt"
        finally:
            app.dependency_overrides.clear()

    @patch("api.routes.resume.ProfileUpdateService")
    def test_confirm_resume_changes_api(self, mock_update_svc_cls, client):
        from api.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {
            "username": "employee1", "role": "EMPLOYEE", "employee_id": 1
        }
        try:
            mock_svc = MagicMock()
            mock_svc.confirm_and_apply_updates.return_value = {
                "status": "SUCCESS",
                "employee_id": 1,
                "applied_updates": {"skills_added_or_upgraded": 1, "certifications_added": 0, "projects_added": 0},
            }
            mock_update_svc_cls.return_value = mock_svc

            payload = {
                "confirmed_skills": [{"skill_name": "Docker", "suggested_level": 3}],
                "confirmed_certifications": [],
                "confirmed_projects": [],
            }
            response = client.post("/employee/me/resume/confirm", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"
        finally:
            app.dependency_overrides.clear()
