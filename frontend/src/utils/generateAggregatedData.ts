import { CATEGORICAL_VALUES, VALUE_WEIGHTS } from './columnMapping';

// Helper function to select value based on weights
function weightedRandom(weights: Record<string, number>): string {
  const items = Object.keys(weights);
  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
  let random = Math.random() * totalWeight;

  for (const item of items) {
    random -= weights[item];
    if (random <= 0) {
      return item;
    }
  }
  return items[items.length - 1];
}

// Helper function to select random value from array
function randomChoice<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

// Generate a single claim with categorical data
export function generateClaim(index: number, year: number): Record<string, any> {
  const month = Math.floor(Math.random() * 12) + 1;
  const day = Math.floor(Math.random() * 28) + 1;
  const claimDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  // Settlement calculations
  const settlementDays = Math.floor(Math.random() * 730) + 30; // 30-760 days
  const settlementMonths = Math.round(settlementDays / 30);
  const settlementYears = settlementMonths / 12;

  // Financial data
  const dollarAmount = Math.floor(Math.random() * 150000) + 2500; // $2,500 - $152,500
  const predictedAmount = dollarAmount * (0.7 + Math.random() * 0.6); // 70%-130% of actual
  const variancePct = ((dollarAmount - predictedAmount) / predictedAmount) * 100;

  // Scores and ratings
  const severityScore = Math.random() * 10; // 0-10
  const cautionLevel = severityScore > 7 ? 'High' : severityScore > 4 ? 'Medium' : 'Low';

  // Geographic data
  const counties = ['Los Angeles', 'San Francisco', 'San Diego', 'Orange', 'Sacramento', 'Alameda', 'Riverside', 'San Bernardino'];
  const states = ['CA', 'NY', 'TX', 'FL', 'IL'];
  const venueRatings = ['Plaintiff Friendly', 'Neutral', 'Defense Friendly'];

  // Adjusters
  const adjusters = ['Smith, John', 'Johnson, Sarah', 'Williams, Mike', 'Brown, Lisa', 'Davis, Tom', 'Miller, Amy', 'Wilson, Bob', 'Moore, Jane'];

  // Injury data
  const injuryGroups = ['Spinal', 'Orthopedic', 'Soft Tissue', 'Head/Brain', 'Multiple'];
  const bodyParts = ['Back', 'Neck', 'Knee', 'Shoulder', 'Head', 'Hip', 'Ankle'];
  const injuries = ['Strain/Sprain', 'Fracture', 'Contusion', 'Laceration', 'Herniated Disc'];

  // Generate categorical fields with weighted distributions
  const claim: Record<string, any> = {
    // Core identifiers
    claim_id: `CLM-${year}-${String(index).padStart(6, '0')}`,
    VERSIONID: 1,
    claim_date: claimDate,
    DURATIONTOREPORT: Math.floor(Math.random() * 30) + 1,
    DOLLARAMOUNTHIGH: dollarAmount,

    // Injury classification
    ALL_BODYPARTS: bodyParts.slice(0, Math.floor(Math.random() * 3) + 1).join(', '),
    ALL_INJURIES: injuries.slice(0, Math.floor(Math.random() * 2) + 1).join(', '),
    ALL_INJURYGROUP_CODES: injuryGroups.slice(0, Math.floor(Math.random() * 2) + 1).join(', '),
    ALL_INJURYGROUP_TEXTS: injuryGroups.slice(0, Math.floor(Math.random() * 2) + 1).join(', '),
    PRIMARY_INJURY: randomChoice(injuries),
    PRIMARY_BODYPART: randomChoice(bodyParts),
    PRIMARY_INJURYGROUP_CODE: randomChoice(injuryGroups),
    INJURY_COUNT: Math.floor(Math.random() * 5) + 1,
    BODYPART_COUNT: Math.floor(Math.random() * 4) + 1,
    INJURYGROUP_COUNT: Math.floor(Math.random() * 3) + 1,

    // Settlement timing
    SETTLEMENT_DAYS: settlementDays,
    SETTLEMENT_MONTHS: settlementMonths,
    SETTLEMENT_YEARS: parseFloat(settlementYears.toFixed(2)),

    // Geographic and venue
    IMPACT: Math.floor(Math.random() * 3) + 1, // 1=Minimal, 2=Moderate, 3=Heavy
    COUNTYNAME: randomChoice(counties),
    VENUESTATE: randomChoice(states),
    VENUE_RATING: randomChoice(venueRatings),
    RATINGWEIGHT: Math.random() * 2 - 1, // -1 to 1

    // Classification
    INJURY_GROUP_CODE: randomChoice(injuryGroups),
    CAUSATION__HIGH_RECOMMENDATION: Math.random(),
    SEVERITY_SCORE: parseFloat(severityScore.toFixed(2)),
    CAUTION_LEVEL: cautionLevel,

    // Business data
    adjuster: randomChoice(adjusters),
    predicted_pain_suffering: parseFloat(predictedAmount.toFixed(2)),
    variance_pct: parseFloat(variancePct.toFixed(2)),

    // Causation factors (numeric 0-1)
    causation_probability: Math.random(),
    causation_tx_delay: Math.random(),
    causation_tx_gaps: Math.random(),
    causation_compliance: Math.random(),

    // Severity factors (numeric 0-1)
    severity_allowed_tx_period: Math.random(),
    severity_initial_tx: Math.random(),
    severity_injections: Math.random(),
    severity_objective_findings: Math.random(),
    severity_pain_mgmt: Math.random(),
    severity_type_tx: Math.random(),
    severity_injury_site: Math.random(),
    severity_code: Math.random(),
  };

  // Add categorical clinical fields with weighted distribution
  claim.Advanced_Pain_Treatment = weightedRandom(VALUE_WEIGHTS.Advanced_Pain_Treatment);
  claim.Causation_Compliance = weightedRandom(VALUE_WEIGHTS.Causation_Compliance);
  claim.Clinical_Findings = weightedRandom(VALUE_WEIGHTS.Clinical_Findings);

  if (Math.random() > 0.95) {
    claim.Cognitive_Symptoms = weightedRandom(VALUE_WEIGHTS.Cognitive_Symptoms);
  }

  if (Math.random() > 0.97) {
    claim.Complete_Disability_Duration = randomChoice(CATEGORICAL_VALUES.Complete_Disability_Duration);
  }

  if (Math.random() > 0.99) {
    claim.Concussion_Diagnosis = randomChoice(CATEGORICAL_VALUES.Concussion_Diagnosis);
  }

  if (Math.random() > 0.98) {
    claim.Consciousness_Impact = randomChoice(CATEGORICAL_VALUES.Consciousness_Impact);
  }

  claim.Consistent_Mechanism = Math.random() > 0.15 ? 'Consistent' : Math.random() > 0.2 ? 'Questionable' : 'Highly Unlikely';

  if (Math.random() > 0.99) {
    claim.Dental_Procedure = randomChoice(CATEGORICAL_VALUES.Dental_Procedure);
    if (claim.Dental_Procedure === 'Yes') {
      claim.Dental_Treatment = randomChoice(CATEGORICAL_VALUES.Dental_Treatment);
      claim.Dental_Visibility = randomChoice(CATEGORICAL_VALUES.Dental_Visibility);
    }
  }

  if (Math.random() > 0.94) {
    claim.Emergency_Treatment = weightedRandom(VALUE_WEIGHTS.Emergency_Treatment);
  }

  if (Math.random() > 0.97) {
    claim.Fixation_Method = randomChoice(CATEGORICAL_VALUES.Fixation_Method);
  }

  if (Math.random() > 0.91) {
    claim.Head_Trauma = weightedRandom(VALUE_WEIGHTS.Head_Trauma);
  }

  if (Math.random() > 0.77) {
    claim.Immobilization_Used = randomChoice(CATEGORICAL_VALUES.Immobilization_Used);
  }

  claim.Injury_Count = randomChoice(CATEGORICAL_VALUES.Injury_Count);
  claim.Injury_Extent = weightedRandom(VALUE_WEIGHTS.Injury_Extent);
  claim.Injury_Laterality = randomChoice(CATEGORICAL_VALUES.Injury_Laterality);
  claim.Injury_Location = randomChoice(CATEGORICAL_VALUES.Injury_Location);
  claim.Injury_Type = randomChoice(CATEGORICAL_VALUES.Injury_Type);

  if (Math.random() > 0.99) {
    claim.Mobility_Assistance = randomChoice(CATEGORICAL_VALUES.Mobility_Assistance);
  }

  claim.Movement_Restriction = weightedRandom(VALUE_WEIGHTS.Movement_Restriction);
  claim.Nerve_Involvement = weightedRandom(VALUE_WEIGHTS.Nerve_Involvement);
  claim.Pain_Management = weightedRandom(VALUE_WEIGHTS.Pain_Management);

  if (Math.random() > 0.98) {
    claim.Partial_Disability_Duration = randomChoice(CATEGORICAL_VALUES.Partial_Disability_Duration);
  }

  claim.Physical_Symptoms = randomChoice(CATEGORICAL_VALUES.Physical_Symptoms);
  claim.Physical_Therapy = weightedRandom(VALUE_WEIGHTS.Physical_Therapy);
  claim.Prior_Treatment = weightedRandom(VALUE_WEIGHTS.Prior_Treatment);
  claim.Recovery_Duration = randomChoice(CATEGORICAL_VALUES.Recovery_Duration);

  if (Math.random() > 0.99) {
    claim.Repair_Type = randomChoice(CATEGORICAL_VALUES.Repair_Type);
  }

  if (Math.random() > 0.99) {
    claim.Respiratory_Issues = randomChoice(CATEGORICAL_VALUES.Respiratory_Issues);
  }

  if (Math.random() > 0.96) {
    claim.Soft_Tissue_Damage = randomChoice(CATEGORICAL_VALUES.Soft_Tissue_Damage);
  }

  if (Math.random() > 0.99) {
    claim.Special_Treatment = randomChoice(CATEGORICAL_VALUES.Special_Treatment);
  }

  if (Math.random() > 0.96) {
    claim.Surgical_Intervention = randomChoice(CATEGORICAL_VALUES.Surgical_Intervention);
  }

  claim.Symptom_Timeline = randomChoice(CATEGORICAL_VALUES.Symptom_Timeline);
  claim.Treatment_Course = weightedRandom(VALUE_WEIGHTS.Treatment_Course);
  claim.Treatment_Delays = weightedRandom(VALUE_WEIGHTS.Treatment_Delays);
  claim.Treatment_Level = randomChoice(CATEGORICAL_VALUES.Treatment_Level);
  claim.Treatment_Period_Considered = randomChoice(CATEGORICAL_VALUES.Treatment_Period_Considered);
  claim.Vehicle_Impact = weightedRandom(VALUE_WEIGHTS.Vehicle_Impact);

  return claim;
}

// Generate full dataset
export function generateClaimsDataset(count: number): Record<string, any>[] {
  const claims: Record<string, any>[] = [];
  const years = [2023, 2024, 2025];

  for (let i = 0; i < count; i++) {
    const year = randomChoice(years);
    claims.push(generateClaim(i + 1, year));
  }

  return claims;
}

// Convert claims to CSV format
export function convertToCSV(claims: Record<string, any>[]): string {
  if (claims.length === 0) return '';

  const headers = Object.keys(claims[0]);
  const csvLines = [headers.join(',')];

  for (const claim of claims) {
    const values = headers.map(header => {
      const value = claim[header];
      if (value === null || value === undefined) return '';

      // Escape values containing commas, quotes, or newlines
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    });
    csvLines.push(values.join(','));
  }

  return csvLines.join('\n');
}

// Create aggregated summary by different dimensions
export function createAggregatedSummaries(claims: Record<string, any>[]) {
  // 1. Summary by Year and Severity
  const yearSeveritySummary: Record<string, any>[] = [];
  const yearSeverityMap = new Map<string, any>();

  claims.forEach(claim => {
    const year = new Date(claim.claim_date).getFullYear();
    const key = `${year}-${claim.CAUTION_LEVEL}`;

    if (!yearSeverityMap.has(key)) {
      yearSeverityMap.set(key, {
        year,
        caution_level: claim.CAUTION_LEVEL,
        count: 0,
        total_settlement: 0,
        total_predicted: 0,
        avg_days: 0,
        total_days: 0,
      });
    }

    const summary = yearSeverityMap.get(key);
    summary.count++;
    summary.total_settlement += claim.DOLLARAMOUNTHIGH;
    summary.total_predicted += claim.predicted_pain_suffering;
    summary.total_days += claim.SETTLEMENT_DAYS;
  });

  yearSeverityMap.forEach(summary => {
    yearSeveritySummary.push({
      year: summary.year,
      caution_level: summary.caution_level,
      claim_count: summary.count,
      avg_settlement: Math.round(summary.total_settlement / summary.count),
      avg_predicted: Math.round(summary.total_predicted / summary.count),
      avg_days: Math.round(summary.total_days / summary.count),
      total_settlement: summary.total_settlement,
    });
  });

  // 2. Summary by County and Year
  const countyYearSummary: Record<string, any>[] = [];
  const countyYearMap = new Map<string, any>();

  claims.forEach(claim => {
    const year = new Date(claim.claim_date).getFullYear();
    const key = `${claim.COUNTYNAME}-${year}`;

    if (!countyYearMap.has(key)) {
      countyYearMap.set(key, {
        county: claim.COUNTYNAME,
        year,
        count: 0,
        total_settlement: 0,
        high_variance_count: 0,
      });
    }

    const summary = countyYearMap.get(key);
    summary.count++;
    summary.total_settlement += claim.DOLLARAMOUNTHIGH;
    if (Math.abs(claim.variance_pct) > 25) {
      summary.high_variance_count++;
    }
  });

  countyYearMap.forEach(summary => {
    countyYearSummary.push({
      county: summary.county,
      year: summary.year,
      claim_count: summary.count,
      total_settlement: summary.total_settlement,
      avg_settlement: Math.round(summary.total_settlement / summary.count),
      high_variance_pct: Math.round((summary.high_variance_count / summary.count) * 100),
    });
  });

  // 3. Summary by Injury Type
  const injuryTypeSummary: Record<string, any>[] = [];
  const injuryTypeMap = new Map<string, any>();

  claims.forEach(claim => {
    const key = claim.INJURY_GROUP_CODE;

    if (!injuryTypeMap.has(key)) {
      injuryTypeMap.set(key, {
        injury_group: key,
        count: 0,
        total_settlement: 0,
        total_days: 0,
      });
    }

    const summary = injuryTypeMap.get(key);
    summary.count++;
    summary.total_settlement += claim.DOLLARAMOUNTHIGH;
    summary.total_days += claim.SETTLEMENT_DAYS;
  });

  injuryTypeMap.forEach(summary => {
    injuryTypeSummary.push({
      injury_group: summary.injury_group,
      claim_count: summary.count,
      avg_settlement: Math.round(summary.total_settlement / summary.count),
      avg_days_to_settlement: Math.round(summary.total_days / summary.count),
      total_settlement: summary.total_settlement,
    });
  });

  // 4. Summary by Treatment Type
  const treatmentSummary: Record<string, any>[] = [];
  const treatmentMap = new Map<string, any>();

  claims.forEach(claim => {
    if (!claim.Treatment_Course) return;

    const key = claim.Treatment_Course;

    if (!treatmentMap.has(key)) {
      treatmentMap.set(key, {
        treatment_course: key,
        count: 0,
        total_settlement: 0,
        avg_severity: 0,
        total_severity: 0,
      });
    }

    const summary = treatmentMap.get(key);
    summary.count++;
    summary.total_settlement += claim.DOLLARAMOUNTHIGH;
    summary.total_severity += claim.SEVERITY_SCORE;
  });

  treatmentMap.forEach(summary => {
    treatmentSummary.push({
      treatment_course: summary.treatment_course,
      claim_count: summary.count,
      avg_settlement: Math.round(summary.total_settlement / summary.count),
      avg_severity_score: (summary.total_severity / summary.count).toFixed(2),
      total_settlement: summary.total_settlement,
    });
  });

  return {
    yearSeveritySummary,
    countyYearSummary,
    injuryTypeSummary,
    treatmentSummary,
  };
}
