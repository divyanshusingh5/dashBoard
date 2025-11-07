export interface ClaimData {
  // Core identifiers - ACTUAL DATA FORMAT
  CLAIMID: number;
  EXPSR_NBR: string;

  // Dates
  CLAIMCLOSEDDATE: string;
  INCIDENTDATE: string;

  // Financial
  CAUSATION_HIGH_RECOMMENDATION: number;
  SETTLEMENTAMOUNT: number;
  DOLLARAMOUNTHIGH: number;
  GENERALS: number;

  // Version and duration
  VERSIONID: number;
  DURATIONTOREPORT: number;

  // Person information
  ADJUSTERNAME: string;
  HASATTORNEY: string | number;
  AGE: number;
  GENDER: string | number;
  OCCUPATION_AVAILABLE: number;
  OCCUPATION?: string;

  // Injury information
  ALL_BODYPARTS: string;
  ALL_INJURIES: string;
  ALL_INJURYGROUP_CODES: string;
  ALL_INJURYGROUP_TEXTS: string;
  PRIMARY_INJURY: string;
  PRIMARY_BODYPART: string;
  PRIMARY_INJURYGROUP_CODE: string;
  INJURY_COUNT: number;
  BODYPART_COUNT: number;
  INJURYGROUP_COUNT: number;
  BODY_REGION: string;

  // Settlement timing
  SETTLEMENT_DAYS: number;
  SETTLEMENT_MONTHS: number;
  SETTLEMENT_YEARS: number;
  SETTLEMENT_SPEED_CATEGORY: string;

  // Location and venue
  IOL: number;  // Impact on Life (was IMPACT)
  COUNTYNAME: string;
  VENUESTATE: string;
  VENUERATINGTEXT: string;
  VENUERATINGPOINT: number;
  RATINGWEIGHT: number;
  VENUERATING: string;
  VULNERABLECLAIMANT?: string;

  // Calculated fields
  SEVERITY_SCORE?: number;
  CAUTION_LEVEL?: string;
  variance_pct?: number;
  // Extended clinical factors
  Advanced_Pain_Treatment?: string;
  Causation_Compliance?: string;
  Clinical_Findings?: string;
  Cognitive_Symptoms?: string;
  Complete_Disability_Duration?: string;
  Concussion_Diagnosis?: string;
  Consciousness_Impact?: string;
  Consistent_Mechanism?: string;
  Dental_Procedure?: string;
  Dental_Treatment?: string;
  Dental_Visibility?: string;
  Emergency_Treatment?: string;
  Fixation_Method?: string;
  Head_Trauma?: string;
  Immobilization_Used?: string;
  Injury_Count?: string;
  Injury_Extent?: string;
  Injury_Laterality?: string;
  Injury_Location?: string;
  Injury_Type?: string;
  Mobility_Assistance?: string;
  Movement_Restriction?: string;
  Nerve_Involvement?: string;
  Pain_Management?: string;
  Partial_Disability_Duration?: string;
  Physical_Symptoms?: string;
  Physical_Therapy?: string;
  Prior_Treatment?: string;
  Recovery_Duration?: string;
  Repair_Type?: string;
  Respiratory_Issues?: string;
  Soft_Tissue_Damage?: string;
  Special_Treatment?: string;
  Surgical_Intervention?: string;
  Symptom_Timeline?: string;
  Treatment_Compliance?: string;
  Treatment_Course?: string;
  Treatment_Delays?: string;
  Treatment_Level?: string;
  Treatment_Period_Considered?: string;
  Vehicle_Impact?: string;
}

export interface FilterState {
  version?: string;  // NEW: Version filter
  injuryGroupCode: string;
  county: string;
  severityScore: string;
  cautionLevel: string;
  venueRating: string;
  impact: string;
  year: string;
}

export type TabType = 'overview' | 'recommendations' | 'alignment' | 'injury' | 'adjuster' | 'venue' | 'recalibration';

// Weight configuration interfaces
export interface WeightConfig {
  factor_name: string;
  base_weight: number;
  min_weight: number;
  max_weight: number;
  category: 'Causation' | 'Severity' | 'Treatment' | 'Clinical' | 'Disability';
  description: string;
  recommended_weight?: number; // Dynamically calculated, not in CSV
  optimal_weight?: number; // Calculated via optimization algorithm
}

export interface WeightAdjustment {
  factor_name: string;
  original_weight: number;
  adjusted_weight: number;
  impact_score?: number;
}

export interface RecalibrationResult {
  claim_id: string;
  original_prediction: number;
  recalibrated_prediction: number;
  actual_value: number;
  original_variance_pct: number;
  recalibrated_variance_pct: number;
  improvement_pct: number;
}

export interface WeightOptimizationRecommendation {
  factor_name: string;
  current_weight: number;
  suggested_weight: number;
  reason: string;
  expected_improvement: number;
  confidence: 'high' | 'medium' | 'low';
}

export interface RecalibrationMetrics {
  total_claims: number;
  improved_count: number;
  degraded_count: number;
  unchanged_count: number;
  avg_improvement_pct: number;
  mape_before: number;
  mape_after: number;
  rmse_before: number;
  rmse_after: number;
}
