"""
ML Promotion Prediction Pydantic schemas.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: Optional[int] = Field(None, description="Employee primary key ID")
    current_grade: Optional[str] = Field(None, description="Employee current job grade (e.g. G2)")
    target_grade: Optional[str] = Field(None, description="Employee target promotion grade (e.g. G3)")
    promotion_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted promotion probability (0.00-1.00)")
    prediction: str = Field(..., description="Classification label ('Likely Progression' or 'Unlikely Progression')")
    model_name: str = Field(..., description="Machine learning classifier model name")
