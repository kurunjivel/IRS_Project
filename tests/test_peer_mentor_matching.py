"""
Unit and integration tests for Phase 8 — Automated Peer & Mentor Matching Network.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from models.employee import Employee
from services.mentor_matching_service import (
    MentorMatchingService,
    MentorMatchResult,
    CoveredSkillGap,
)
from services.career_service import CareerService
from api.main import app


@pytest.fixture
def mock_employee():
    return Employee(
        employee_id=1,
        employee_code="EMP001",
        full_name="John Doe",
        email="john.doe@example.com",
        department="Engineering",
        experience_years=3.5,
        performance_rating=4.2,
        joining_date="2022-01-15",
        current_grade="G2",
        current_grade_id=2,
        target_grade="G3",
        target_grade_id=3,
        skills=[],
        certifications=[],
        projects=[],
    )


@pytest.fixture
def sample_skill_gaps():
    return [
        {
            "skill": "Flask",
            "category": "Backend",
            "current_level": 0,
            "required_level": 3,
            "gap": 3,
            "mandatory": True,
        },
        {
            "skill": "Docker",
            "category": "DevOps",
            "current_level": 1,
            "required_level": 3,
            "gap": 2,
            "mandatory": True,
        },
        {
            "skill": "AWS",
            "category": "Cloud",
            "current_level": 0,
            "required_level": 3,
            "gap": 3,
            "mandatory": False,
        },
    ]


@pytest.fixture
def sample_candidates():
    return [
        {
            "employee_id": 1,  # Self (should be filtered out)
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "department": "Engineering",
            "current_grade": "G2",
            "current_grade_id": 2,
            "performance_rating": 4.2,
            "experience_years": 3.5,
        },
        {
            "employee_id": 2,  # Senior Mentor (G3)
            "full_name": "Alice Smith",
            "email": "alice.smith@example.com",
            "department": "Engineering",
            "current_grade": "G3",
            "current_grade_id": 3,
            "performance_rating": 4.8,
            "experience_years": 6.0,
        },
        {
            "employee_id": 3,  # Peer Partner (G2)
            "full_name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "department": "Engineering",
            "current_grade": "G2",
            "current_grade_id": 2,
            "performance_rating": 4.0,
            "experience_years": 4.0,
        },
        {
            "employee_id": 4,  # Junior Employee (G1 - should be filtered out)
            "full_name": "Charlie Brown",
            "email": "charlie@example.com",
            "department": "Engineering",
            "current_grade": "G1",
            "current_grade_id": 1,
            "performance_rating": 3.5,
            "experience_years": 1.0,
        },
    ]


class TestMentorMatchingService:

    @patch("services.mentor_matching_service.EmployeeRepository")
    @patch("services.mentor_matching_service.RecommendationRepository")
    def test_find_matches_eligibility_and_ranking(
        self, mock_rec_repo_cls, mock_emp_repo_cls, mock_employee, sample_skill_gaps, sample_candidates
    ):
        mock_emp_repo = MagicMock()
        mock_emp_repo.get_all_employees.return_value = sample_candidates

        # Mock skills for senior mentor Alice (employee 2)
        mock_emp_repo.get_employee_skills.side_effect = lambda emp_id: (
            [
                {"skill_name": "Flask", "skill_level": 4, "category": "Backend"},
                {"skill_name": "Docker", "skill_level": 3, "category": "DevOps"},
            ]
            if emp_id == 2
            else [
                {"skill_name": "FastAPI", "skill_level": 4, "category": "Backend"},
            ]
            if emp_id == 3
            else []
        )

        mock_emp_repo.get_employee_projects.return_value = [
            {"project_name": "Cloud Portal", "lead_project": True, "duration_months": 18}
        ]
        mock_emp_repo.get_employee_certifications.return_value = [
            {"certification_name": "AWS Certified Developer", "status": "Completed"}
        ]

        mock_emp_repo_cls.return_value = mock_emp_repo
        mock_rec_repo_cls.return_value = MagicMock()

        matcher = MentorMatchingService(emp_repo=mock_emp_repo)
        matches = matcher.find_matches(mock_employee, skill_gaps=sample_skill_gaps, limit=5)

        # Assertions
        assert len(matches) == 2  # Only Alice (G3) and Bob (G2) eligible
        assert matches[0].mentor_id == 2  # Alice is top match
        assert matches[0].match_type == "MENTOR"
        assert matches[0].match_score > 70.0
        assert len(matches[0].covered_gaps) >= 1

        # Check Bob (Peer)
        assert matches[1].mentor_id == 3
        assert matches[1].match_type == "PEER_LEARNING_PARTNER"

    @patch("services.mentor_matching_service.EmployeeRepository")
    def test_covered_skills_semantic_matching(self, mock_emp_repo_cls, mock_employee):
        mock_emp_repo = MagicMock()
        matcher = MentorMatchingService(emp_repo=mock_emp_repo)

        unmet_gaps = [
            {"skill": "Flask", "required_level": 3, "gap": 3},
        ]
        cand_skills = [
            {"skill_name": "FastAPI", "skill_level": 4, "category": "Backend"},
        ]

        covered, score = matcher._evaluate_skill_gap_coverage(unmet_gaps, cand_skills)

        # FastAPI should semantically match Flask (STRONG_SEMANTIC_MATCH or RELATED_SKILL)
        assert len(covered) == 1
        assert covered[0].required_skill == "Flask"
        assert covered[0].mentor_skill == "FastAPI"
        assert score > 50.0


class TestMentorMatchingAPI:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch("api.routes.mentor_matching.CareerService")
    def test_get_mentor_matches_api(self, mock_career_svc_cls, client):
        mock_svc = MagicMock()
        mock_svc.get_mentor_matches.return_value = {
            "employee_id": 1,
            "full_name": "John Doe",
            "current_grade": "G2",
            "target_grade": "G3",
            "department": "Engineering",
            "total_matches": 1,
            "matches": [
                {
                    "mentor_id": 2,
                    "full_name": "Alice Smith",
                    "match_score": 88.5,
                    "match_level": "EXCELLENT",
                    "match_type": "MENTOR",
                }
            ],
        }
        mock_career_svc_cls.return_value = mock_svc

        response = client.get("/mentors/matches/1?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == 1
        assert len(data["matches"]) == 1
        assert data["matches"][0]["full_name"] == "Alice Smith"

    def test_request_mentorship_api(self, client):
        payload = {
            "employee_id": 1,
            "mentor_id": 2,
            "skill_gap_focus": "Flask",
            "notes": "Looking for mentoring on Flask & Cloud deployment",
        }
        response = client.post("/mentors/request", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["request_details"]["mentor_id"] == 2
