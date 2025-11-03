export interface ClaimData {
  claim_id: string;
  VERSIONID: number;
  claim_date: string;
  DURATIONTOREPORT: number;
  DOLLARAMOUNTHIGH: number;
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
  SETTLEMENT_DAYS: number;
  SETTLEMENT_MONTHS: number;
  SETTLEMENT_YEARS: number;
  IMPACT: number;
  COUNTYNAME: string;
  VENUESTATE: string;
  VENUE_RATING: string;
  RATINGWEIGHT: number;
  INJURY_GROUP_CODE: string;
  CAUSATION__HIGH_RECOMMENDATION: number;
  SEVERITY_SCORE: number;
  CAUTION_LEVEL: string;
  adjuster: string;
  predicted_pain_suffering: number;
  variance_pct: number;
  // Causation factors
  causation_probability: number;
  causation_tx_delay: number;
  causation_tx_gaps: number;
  causation_compliance: number;
  // Severity factors
  severity_allowed_tx_period: number;
  severity_initial_tx: number;
  severity_injections: number;
  severity_objective_findings: number;
  severity_pain_mgmt: number;
  severity_type_tx: number;
  severity_injury_site: number;
  severity_code: number;
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
