"""
Pydantic Schemas for Succession Planning and 9-Box Matrix — Phase 1 Enhancement 5.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class NineBoxEmployeeSummary(BaseModel):
    employee_id: int
    full_name: str
    email: str
    department: str
    current_grade: str
    target_grade: str
    performance_rating: float
    readiness_score: float
    performance_level: str
    readiness_level: str
    pipeline_indicator: str


class NineBoxCell(BaseModel):
    box_id: str
    title: str
    performance_level: str
    readiness_level: str
    color: str
    description: str
    indicator: str
    count: int
    percentage: float
    employees: List[NineBoxEmployeeSummary]


class NineBoxMatrixResponse(BaseModel):
    total_analyzed: int
    filters: Dict[str, Optional[Any]] = Field(default_factory=dict)
    pipeline_summary: Dict[str, int]
    grid: Dict[str, NineBoxCell]
