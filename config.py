"""
Database and system configuration for the IRS project.
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "irs_db",
}

POOL_CONFIG = {
    "pool_name": "irs_pool",
    "pool_size": 5,
}

SEMANTIC_MATCHING_CONFIG = {
    "enabled": True,
    "model_name": "all-MiniLM-L6-v2",
    "chroma_db_path": "./.chroma_db",
    "thresholds": {
        "STRONG_SEMANTIC_MATCH": 0.85,
        "RELATED_SKILL": 0.70,
        "PARTIAL_RELEVANCE": 0.55,
        "INSUFFICIENT_MATCH": 0.00,
    },
}

ATTRITION_RISK_CONFIG = {
    "enabled": True,
    "model_version": "attrition_data_readiness_v1",
    "thresholds": {
        "LOW_MAX": 0.35,
        "MODERATE_MAX": 0.65,
    },
}