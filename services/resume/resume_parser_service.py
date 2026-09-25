"""
Resume/CV Parsing & Candidate Extraction Service.

Extracts structured skills, certifications, and project experience from raw text.
Compares extracted entities against existing employee profile to generate candidate updates diff.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.employee import Employee
from database.employee_repository import EmployeeRepository
from services.semantic.semantic_matcher import SemanticMatcher

logger = logging.getLogger(__name__)


# Standard IRS Skill Catalog mapping with categories
STANDARD_SKILL_CATALOG = {
    "python": {"name": "Python", "category": "Backend"},
    "fastapi": {"name": "FastAPI", "category": "Backend"},
    "flask": {"name": "Flask", "category": "Backend"},
    "django": {"name": "Django", "category": "Backend"},
    "java": {"name": "Java", "category": "Backend"},
    "spring": {"name": "Spring Boot", "category": "Backend"},
    "sql": {"name": "SQL", "category": "Database"},
    "postgresql": {"name": "PostgreSQL", "category": "Database"},
    "mysql": {"name": "MySQL", "category": "Database"},
    "mongodb": {"name": "MongoDB", "category": "Database"},
    "docker": {"name": "Docker", "category": "DevOps"},
    "kubernetes": {"name": "Kubernetes", "category": "DevOps"},
    "aws": {"name": "AWS", "category": "Cloud"},
    "azure": {"name": "Azure", "category": "Cloud"},
    "gcp": {"name": "Google Cloud", "category": "Cloud"},
    "react": {"name": "React", "category": "Frontend"},
    "javascript": {"name": "JavaScript", "category": "Frontend"},
    "typescript": {"name": "TypeScript", "category": "Frontend"},
    "html": {"name": "HTML/CSS", "category": "Frontend"},
    "css": {"name": "HTML/CSS", "category": "Frontend"},
    "git": {"name": "Git", "category": "DevOps"},
    "ci/cd": {"name": "CI/CD", "category": "DevOps"},
    "scikit-learn": {"name": "Scikit-Learn", "category": "Data Science"},
    "pandas": {"name": "Pandas", "category": "Data Science"},
    "numpy": {"name": "NumPy", "category": "Data Science"},
    "tensorflow": {"name": "TensorFlow", "category": "AI/ML"},
    "pytorch": {"name": "PyTorch", "category": "AI/ML"},
}

KNOWN_CERTIFICATIONS = [
    "AWS Certified Solutions Architect",
    "AWS Certified Developer",
    "AWS Certified SysOps Administrator",
    "Docker Certified Associate",
    "Certified Kubernetes Administrator",
    "Microsoft Certified: Azure Developer",
    "Google Associate Cloud Engineer",
    "Oracle Certified Professional Java SE",
    "Scrum Master Certified",
    "PMP",
]


@dataclass
class CandidateSkillUpdate:
    skill_name: str
    suggested_level: int
    current_level: int = 0
    category: str = "General"
    is_new: bool = True
    match_confidence: float = 1.0


@dataclass
class CandidateCertUpdate:
    certification_name: str
    status: str = "Completed"
    is_new: bool = True


@dataclass
class CandidateProjectUpdate:
    project_name: str
    role_description: str = ""
    is_new: bool = True


@dataclass
class ResumeParseResult:
    filename: str
    extracted_sections: List[str]
    candidate_changes: Dict[str, Any]
    raw_preview: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "extracted_sections": self.extracted_sections,
            "candidate_changes": self.candidate_changes,
            "raw_preview": self.raw_preview,
        }


class ResumeParserService:
    """
    Parses resume text, extracts entities, and compares against employee profile.
    """

    def __init__(self, emp_repo: Optional[EmployeeRepository] = None) -> None:
        self.emp_repo = emp_repo or EmployeeRepository()
        self.semantic_matcher = SemanticMatcher()

    def parse_resume_text(
        self, text: str, filename: str, employee_id: int
    ) -> ResumeParseResult:
        """
        Extract professional data from text and compare with existing profile.

        Args:
            text: Extracted raw text.
            filename: Original resume filename.
            employee_id: Employee ID to compare against.

        Returns:
            ResumeParseResult with candidate changes diff.
        """
        # Fetch existing employee profile data
        emp_dict = self.emp_repo.get_employee(employee_id)
        if not emp_dict:
            raise ValueError(f"Employee with ID {employee_id} not found.")

        existing_skills = self.emp_repo.get_employee_skills(employee_id)
        existing_certs = self.emp_repo.get_employee_certifications(employee_id)
        existing_projects = self.emp_repo.get_employee_projects(employee_id)

        # 1. Section Identification
        sections = self._detect_sections(text)

        # 2. Extract Entities
        extracted_skills = self._extract_skills(text)
        extracted_certs = self._extract_certifications(text)
        extracted_projects = self._extract_projects(text)

        # 3. Compare with existing profile (Diff calculation)
        candidate_changes = self._compare_with_profile(
            extracted_skills,
            extracted_certs,
            extracted_projects,
            existing_skills,
            existing_certs,
            existing_projects,
        )

        preview = text[:400] + ("..." if len(text) > 400 else "")

        return ResumeParseResult(
            filename=filename,
            extracted_sections=list(sections.keys()),
            candidate_changes=candidate_changes,
            raw_preview=preview,
        )

    def _detect_sections(self, text: str) -> Dict[str, str]:
        """Detect standard sections in resume text."""
        sections = {}
        patterns = {
            "Skills": r"(?i)(skills|technical skills|core competencies)",
            "Experience": r"(?i)(experience|work experience|employment history)",
            "Projects": r"(?i)(projects|key projects|key accomplishments)",
            "Certifications": r"(?i)(certifications|licenses|credentials)",
            "Education": r"(?i)(education|academic qualification)",
        }
        for sec_name, pat in patterns.items():
            if re.search(pat, text):
                sections[sec_name] = "Detected"
        return sections

    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills and estimate proficiency level from text context."""
        found_skills: Dict[str, Dict[str, Any]] = {}
        text_lower = text.lower()

        for key, info in STANDARD_SKILL_CATALOG.items():
            # Use regex word boundary check
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, text_lower):
                s_name = info["name"]
                cat = info["category"]
                
                # Estimate proficiency based on experience keyword indicators
                level = 3  # default proficiency level
                if re.search(r"\b(senior|expert|lead|advanced)\b.*" + re.escape(key), text_lower) or \
                   re.search(re.escape(key) + r".*\b(5\+|5 years|expert|advanced)\b", text_lower):
                    level = 4
                elif re.search(r"\b(architect|principal|master)\b.*" + re.escape(key), text_lower):
                    level = 5
                elif re.search(r"\b(junior|basic|beginner)\b.*" + re.escape(key), text_lower):
                    level = 2

                found_skills[s_name] = {
                    "skill_name": s_name,
                    "category": cat,
                    "suggested_level": level,
                }

        return list(found_skills.values())

    def _extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Extract certifications from text."""
        found_certs = []
        text_lower = text.lower()
        for cert in KNOWN_CERTIFICATIONS:
            if cert.lower() in text_lower:
                found_certs.append({
                    "certification_name": cert,
                    "status": "Completed",
                })
        return found_certs

    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project mentions from text."""
        found_projects = []
        # Look for project block bullet patterns
        proj_matches = re.findall(r"(?i)project[:\s]+([^\n\.]+)", text)
        for pm in proj_matches[:3]:
            title = pm.strip()
            if len(title) > 3 and len(title) < 60:
                found_projects.append({
                    "project_name": title,
                    "role_description": "Extracted from resume",
                })
        return found_projects

    def _compare_with_profile(
        self,
        extracted_skills: List[Dict[str, Any]],
        extracted_certs: List[Dict[str, Any]],
        extracted_projects: List[Dict[str, Any]],
        existing_skills: List[Dict[str, Any]],
        existing_certs: List[Dict[str, Any]],
        existing_projects: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate diff comparing extracted resume items against existing employee profile."""

        # Map existing skills by name lower
        ex_skills_map = {s["skill_name"].lower(): s.get("skill_level", 0) for s in existing_skills}
        ex_certs_set = {c["certification_name"].lower() for c in existing_certs}
        ex_proj_set = {p["project_name"].lower() for p in existing_projects}

        new_skills = []
        upgraded_skills = []
        unchanged_skills = []

        for sk in extracted_skills:
            name = sk["skill_name"]
            name_lower = name.lower()
            sugg_lvl = sk["suggested_level"]
            cat = sk["category"]

            if name_lower not in ex_skills_map:
                new_skills.append({
                    "skill_name": name,
                    "suggested_level": sugg_lvl,
                    "current_level": 0,
                    "category": cat,
                    "action": "ADD_NEW_SKILL",
                })
            else:
                curr_lvl = ex_skills_map[name_lower]
                if sugg_lvl > curr_lvl:
                    upgraded_skills.append({
                        "skill_name": name,
                        "current_level": curr_lvl,
                        "suggested_level": sugg_lvl,
                        "category": cat,
                        "action": "UPGRADE_PROFICIENCY",
                    })
                else:
                    unchanged_skills.append({
                        "skill_name": name,
                        "current_level": curr_lvl,
                        "suggested_level": sugg_lvl,
                        "category": cat,
                        "action": "NO_CHANGE",
                    })

        new_certs = []
        for c in extracted_certs:
            if c["certification_name"].lower() not in ex_certs_set:
                new_certs.append({
                    "certification_name": c["certification_name"],
                    "status": c["status"],
                    "action": "ADD_NEW_CERTIFICATION",
                })

        new_projs = []
        for p in extracted_projects:
            if p["project_name"].lower() not in ex_proj_set:
                new_projs.append({
                    "project_name": p["project_name"],
                    "role_description": p.get("role_description", ""),
                    "action": "ADD_NEW_PROJECT",
                })

        return {
            "new_skills": new_skills,
            "upgraded_skills": upgraded_skills,
            "unchanged_skills": unchanged_skills,
            "new_certifications": new_certs,
            "new_projects": new_projs,
            "total_candidate_updates": len(new_skills) + len(upgraded_skills) + len(new_certs) + len(new_projs),
        }
