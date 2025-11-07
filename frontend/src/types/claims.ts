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

  // NEW: Composite calculated scores from model
  CALCULATED_SEVERITY_SCORE?: number;
  CALCULATED_CAUSATION_SCORE?: number;
  RN?: number;

  // NEW: Multi-tier injury system - By SEVERITY ranking
  PRIMARY_INJURY_BY_SEVERITY?: string;
  PRIMARY_BODYPART_BY_SEVERITY?: string;
  PRIMARY_INJURYGROUP_CODE_BY_SEVERITY?: string;
  PRIMARY_INJURY_SEVERITY_SCORE?: number;
  PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY?: number;

  SECONDARY_INJURY_BY_SEVERITY?: string;
  SECONDARY_BODYPART_BY_SEVERITY?: string;
  SECONDARY_INJURYGROUP_CODE_BY_SEVERITY?: string;
  SECONDARY_INJURY_SEVERITY_SCORE?: number;
  SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY?: number;

  TERTIARY_INJURY_BY_SEVERITY?: string;
  TERTIARY_BODYPART_BY_SEVERITY?: string;
  TERTIARY_INJURY_SEVERITY_SCORE?: number;
  TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY?: number;

  // NEW: Multi-tier injury system - By CAUSATION ranking
  PRIMARY_INJURY_BY_CAUSATION?: string;
  PRIMARY_BODYPART_BY_CAUSATION?: string;
  PRIMARY_INJURYGROUP_CODE_BY_CAUSATION?: string;
  PRIMARY_INJURY_CAUSATION_SCORE?: number;
  PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION?: number;

  SECONDARY_INJURY_BY_CAUSATION?: string;
  SECONDARY_BODYPART_BY_CAUSATION?: string;
  SECONDARY_INJURYGROUP_CODE_BY_CAUSATION?: string;
  SECONDARY_INJURY_CAUSATION_SCORE?: number;
  SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION?: number;

  TERTIARY_INJURY_BY_CAUSATION?: string;
  TERTIARY_BODYPART_BY_CAUSATION?: string;
  TERTIARY_INJURY_CAUSATION_SCORE?: number;
  TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION?: number;

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

// SSNB Data Interface - Float-based clinical factors for weight recalibration
export interface SSNBData {
  CLAIMID: number;
  VERSIONID: number;
  EXPSR_NBR: string;
  DOLLARAMOUNTHIGH: number;
  CAUSATION_HIGH_RECOMMENDATION: number;
  PRIMARY_SEVERITY_SCORE: number;
  PRIMARY_CAUSATION_SCORE: number;
  PRIMARY_INJURY: string;
  PRIMARY_BODYPART: string;
  PRIMARY_INJURY_GROUP: string;

  // Float clinical factors (NOT categorical strings like in Claims table)
  Causation_Compliance: number | null;
  Clinical_Findings: number | null;
  Consistent_Mechanism: number | null;
  Injury_Location: number | null;
  Movement_Restriction: number | null;
  Pain_Management: number | null;
  Prior_Treatment: number | null;
  Symptom_Timeline: number | null;
  Treatment_Course: number | null;
  Treatment_Delays: number | null;
  Treatment_Period_Considered: number | null;
  Vehicle_Impact: number | null;

  // Venue and demographics
  VENUERATING: string;
  RATINGWEIGHT: number | null;
  VENUERATINGTEXT: string | null;
  VENUERATINGPOINT: number | null;
  AGE: number;
  GENDER: number;
  HASATTORNEY: number;
  IOL: number;
  ADJUSTERNAME: string;
  COUNTYNAME: string | null;
  VENUESTATE: string;
}

// Prediction Variance Analysis
export interface PredictionVarianceData {
  CLAIMID: number;
  DOLLARAMOUNTHIGH: number;
  CAUSATION_HIGH_RECOMMENDATION: number;
  variance_pct: number;
  prediction_direction: 'Over' | 'Under';

  // Multi-tier injury data
  PRIMARY_INJURY_BY_SEVERITY: string;
  PRIMARY_BODYPART_BY_SEVERITY: string;
  PRIMARY_INJURY_SEVERITY_SCORE: number;
  PRIMARY_INJURY_BY_CAUSATION: string;
  PRIMARY_BODYPART_BY_CAUSATION: string;
  PRIMARY_INJURY_CAUSATION_SCORE: number;

  // Composite scores
  CALCULATED_SEVERITY_SCORE: number;
  CALCULATED_CAUSATION_SCORE: number;

  // Key clinical factors
  Causation_Compliance: string | null;
  Clinical_Findings: string | null;
  Treatment_Course: string | null;
  Symptom_Timeline: string | null;
  Pain_Management: string | null;
  Movement_Restriction: string | null;

  // Venue and demographics
  VENUERATING: string;
  IOL: number;
  AGE: number;
  HASATTORNEY: string | number;
  ADJUSTERNAME: string;
  COUNTYNAME: string;
  VENUESTATE: string;
}

export interface PredictionVarianceSummary {
  total_bad_predictions: number;
  over_predictions: number;
  under_predictions: number;
  avg_variance_pct?: number;
  max_variance_pct?: number;
  min_variance_pct?: number;
}

export interface PredictionVarianceResponse {
  bad_predictions: PredictionVarianceData[];
  summary: PredictionVarianceSummary;
  filters: {
    variance_threshold: number;
    limit: number;
  };
}

// Factor Combination Analysis
export interface FactorCombination {
  combination_key: string;
  factors: {
    injury_severity: string;
    injury_causation: string;
    venue: string;
    attorney: string;
    ioi: number;
    causation_compliance: string;
    clinical_findings: string;
  };
  count: number;
  avg_variance_pct: number;
  max_variance_pct: number;
  sample_claims: Array<{
    CLAIMID: number;
    variance_pct: number;
    actual: number;
    predicted: number;
  }>;
}

export interface FactorCombinationResponse {
  problematic_combinations: FactorCombination[];
  total_combinations: number;
  filters: {
    variance_threshold: number;
    min_occurrences: number;
  };
  recommendations: string[];
}
