"""
ML Promotion Prediction Pydantic schemas.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FeatureExplanationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feature: str = Field(..., description="Raw feature column name")
    feature_label: str = Field(..., description="Human-readable feature title")
    feature_value: float | str | int | bool = Field(..., description="Value of feature for employee")
    shap_value: float = Field(..., description="SHAP quantitative contribution to probability")
    direction: str = Field(..., description="Contribution direction ('positive', 'negative', 'neutral')")
    explanation: str = Field(..., description="Human-readable explanation sentence")


class ShapAnalysisSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    base_value: float = Field(..., description="Baseline expectation probability")
    positive_factors: list[FeatureExplanationSchema] = Field(default_factory=list, description="Positive contributing factors")
    negative_factors: list[FeatureExplanationSchema] = Field(default_factory=list, description="Negative contributing factors")
    neutral_factors: list[FeatureExplanationSchema] = Field(default_factory=list, description="Neutral contributing factors")
    summary: str = Field("", description="Narrative summary of SHAP analysis")


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: Optional[int] = Field(None, description="Employee primary key ID")
    current_grade: Optional[str] = Field(None, description="Employee current job grade (e.g. G2)")
    target_grade: Optional[str] = Field(None, description="Employee target promotion grade (e.g. G3)")
    promotion_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted promotion probability (0.00-1.00)")
    prediction: str = Field(..., description="Classification label ('Likely Progression' or 'Unlikely Progression')")
    model_name: str = Field(..., description="Machine learning classifier model name")
    shap_analysis: Optional[ShapAnalysisSchema] = Field(None, description="Explainable AI SHAP attributions")
