"""
Skill Normalization Service — Phase 7.

Normalizes skill strings into canonical representations and enriches skill text representation
with domain taxonomy context for accurate semantic embedding similarity matching.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Known domain aliases mapping (lowercase raw string -> canonical string)
SKILL_ALIASES = {
    "fast api": "FastAPI",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "python": "Python",
    "python3": "Python",
    "java": "Java",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
}

# Domain taxonomy descriptions to enrich sentence-transformer embeddings
DOMAIN_TAXONOMY = {
    "FastAPI": "Backend Web API Framework for Microservices and Web Development in Python",
    "Flask": "Backend Web API Framework for Microservices and Web Development in Python",
    "Django": "Backend Web Framework for Python Applications",
    "Express.js": "Backend Web API Framework for Node.js Applications",
    "Node.js": "Backend JavaScript Runtime Environment",
    "React": "Frontend UI Framework and Component Library for Web Applications",
    "Vue.js": "Frontend UI Framework for Web Applications",
    "Angular": "Frontend UI Framework for Web Applications",
    "AWS": "Cloud Infrastructure and Computing Platform",
    "GCP": "Cloud Infrastructure and Computing Platform",
    "Azure": "Cloud Infrastructure and Computing Platform",
    "Docker": "Containerization and DevOps Infrastructure",
    "Kubernetes": "Container Orchestration and DevOps Infrastructure",
    "MySQL": "Relational Database Management System SQL",
    "PostgreSQL": "Relational Database Management System SQL",
    "SQL": "Database Query Language and Relational Database Systems",
    "MongoDB": "NoSQL Document Database Management System",
}

# Distinct programming languages should not transfer partial proficiency credit to each other
PROGRAMMING_LANGUAGES = {"Python", "Java", "Go", "C++", "C#", "Rust", "Ruby", "PHP"}


class SkillNormalizationService:
    """Service to normalize skill names to canonical forms and produce rich embedding texts."""

    @staticmethod
    def normalize(skill_name: str) -> str:
        """
        Convert a raw skill string to its canonical form.
        """
        if not skill_name:
            return ""

        cleaned = skill_name.strip()
        lower_cleaned = cleaned.lower()
        lower_cleaned = re.sub(r"\s+", " ", lower_cleaned)

        if lower_cleaned in SKILL_ALIASES:
            return SKILL_ALIASES[lower_cleaned]

        return cleaned.strip().title()

    @classmethod
    def get_embedding_text(cls, skill_name: str, category: str = None) -> str:
        """
        Produce domain-enriched text representation for embedding generation.
        """
        canonical = cls.normalize(skill_name)
        domain_desc = DOMAIN_TAXONOMY.get(canonical)

        if domain_desc:
            return f"Skill: {canonical}, Domain: {domain_desc}"
        elif category:
            return f"Skill: {canonical}, Domain: {category} Technical Skill"
        return f"Skill: {canonical}"

    @classmethod
    def is_distinct_language_pair(cls, skill1: str, skill2: str) -> bool:
        """
        Check if two skills represent different core programming languages.
        """
        c1 = cls.normalize(skill1)
        c2 = cls.normalize(skill2)
        return c1 in PROGRAMMING_LANGUAGES and c2 in PROGRAMMING_LANGUAGES and c1 != c2
