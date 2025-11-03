from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ClaimBase(BaseModel):
    claim_id: str
    adjuster: Optional[str] = None
    injury_group: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    settlement_year: Optional[int] = None
    settlement_amount: Optional[float] = None
    model_prediction: Optional[float] = None
    consensus_value: Optional[float] = None
    variance: Optional[float] = None

class Claim(ClaimBase):
    class Config:
        from_attributes = True

class ClaimsResponse(BaseModel):
    claims: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int

class AggregatedData(BaseModel):
    data: List[Dict[str, Any]]
    total_records: int

class KPIData(BaseModel):
    total_claims: int
    total_settlement: float
    avg_settlement: float
    avg_variance: float
    avg_variance_pct: float
    median_settlement: float
    total_overestimated: float
    total_underestimated: float

class FilterOptions(BaseModel):
    injury_groups: List[str]
    adjusters: List[str]
    states: List[str]
    counties: List[str]
    years: List[int]

class RecalibrationRequest(BaseModel):
    weights: Dict[str, float]
    claims_data: Optional[List[Dict[str, Any]]] = None

class RecalibrationResponse(BaseModel):
    success: bool
    metrics: Dict[str, Any]
    optimized_weights: Optional[Dict[str, float]] = None
    message: str

class WeightOptimizationRequest(BaseModel):
    claims: List[Dict[str, Any]]
    current_weights: Dict[str, float]
    optimization_method: str = "variance_minimization"

class WeightOptimizationResponse(BaseModel):
    optimized_weights: Dict[str, float]
    improvement_metrics: Dict[str, Any]
    iterations: int
    converged: bool
