import { ClaimData } from "@/types/claims";

export function generateDummyData(): ClaimData[] {
  const counties = ['Los Angeles', 'Cook', 'Harris', 'Maricopa', 'King', 'Miami-Dade', 'Dallas', 'Orange', 'Broward', 'Riverside', 'San Diego', 'Bexar'];
  const states = ['CA', 'IL', 'TX', 'AZ', 'WA', 'FL', 'TX', 'CA', 'FL', 'CA', 'CA', 'TX'];
  const bodyParts = ['Neck/Back', 'Head', 'Shoulder', 'Knee', 'Ankle', 'Wrist', 'Elbow'];
  const injuries = ['Sprain/Strain', 'Fracture', 'Laceration', 'Contusion', 'Minor Closed Head Injury/Mild Concussion'];
  const injuryGroupCodes = ['SSNB', 'MCHI', 'BULG', 'DINB', 'MSUE', 'JFLE'];
  const injuryGroupTexts = ['Sprain/Strain, Neck/Back', 'Minor Closed Head Injury', 'Bulge/Herniation', 'Disc Injury, Neck/Back', 'Muscle/Soft Tissue, Upper Extremity', 'Joint/Flex/Limb Extremity'];
  const adjusters = ['Sarah Williams', 'Mike Johnson', 'Emily Chen', 'David Martinez', 'Lisa Anderson', 'James Wilson'];
  const venueRatings = ['Moderate', 'Conservative', 'Liberal'];
  const cautionLevels = ['Low', 'Medium', 'High'];
  
  // Causation factor weight options
  const causationProbabilityWeights = [0.3257, 0.2212, 0.4478, 0.0000];
  const causationTxDelayWeights = [0.1226, 0.0000];
  const causationTxGapsWeights = [0.1313, 0.0000];
  const causationComplianceWeights = [0.1474, 0.0864];
  
  // Severity factor weight options
  const severityAllowedTxPeriodWeights = [1.4488, 0.0000, 2.3490, 3.1606, 3.8533, 4.3507];
  const severityInitialTxWeights = [1.5445, 1.2406, 0.6738, 0.0000];
  const severityInjectionsWeights = [0.0000, 1.9855, 3.0855, 3.4370, 5.1228];
  const severityObjectiveFindingsWeights = [2.7611, 0.0];
  const severityPainMgmtWeights = [0.0000, 0.6396, 1.1258];
  const severityTypeTxWeights = [2.0592, 3.2501];
  const severityInjurySiteWeights = [1.8450, 1.1767, 0.9862, 0.4866, 0.0000];
  const severityCodeWeights = [0.4864, 0.3803, 0.8746, 0.0000];
  
  const data: ClaimData[] = [];
  
  for (let i = 0; i < 500; i++) {
    let year;
    const r = Math.random();
    if (r < 0.3) year = 2023;
    else if (r < 0.7) year = 2024;
    else year = 2025;
    
    let month = Math.floor(Math.random() * 12) + 1;
    if (year === 2025) month = Math.floor(Math.random() * 9) + 1;
    const day = Math.floor(Math.random() * 28) + 1;
    const claimDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    
    const settlementDays = Math.floor(Math.random() * 350) + 7;
    const settlementMonths = Math.round(settlementDays / 30);
    const settlementYears = parseFloat((settlementDays / 365).toFixed(1));
    
    const severityScore = parseFloat((Math.random() * 12 + 1).toFixed(1));
    const impact = Math.floor(Math.random() * 5);
    const venueRating = venueRatings[Math.floor(Math.random() * 3)];
    const ratingWeight = venueRating === 'Liberal' ? 132 : venueRating === 'Moderate' ? 100 : 80;
    const cautionLevel = cautionLevels[Math.floor(Math.random() * 3)];
    
    const dollarAmountHigh = Math.floor(Math.random() * 150000) + 2500;
    const causationHighRec = parseFloat((0.5 + Math.random() * 0.5).toFixed(2));
    const predicted = dollarAmountHigh * (0.7 + Math.random() * 0.6);
    const variancePct = ((dollarAmountHigh - predicted) / predicted) * 100;
    
    const countyIdx = Math.floor(Math.random() * counties.length);
    const injuryCount = Math.floor(Math.random() * 4) + 1;
    const bodypartCount = Math.floor(Math.random() * 3) + 1;
    const injuryGroupCount = Math.floor(Math.random() * 3) + 1;
    
    // Generate multiple body parts and injuries
    const selectedBodyParts = Array.from({ length: bodypartCount }, () => 
      bodyParts[Math.floor(Math.random() * bodyParts.length)]
    );
    const selectedInjuries = Array.from({ length: injuryCount }, () => 
      injuries[Math.floor(Math.random() * injuries.length)]
    );
    const selectedGroupCodes = Array.from({ length: injuryGroupCount }, () => 
      injuryGroupCodes[Math.floor(Math.random() * injuryGroupCodes.length)]
    );
    const selectedGroupTexts = Array.from({ length: injuryGroupCount }, () => 
      injuryGroupTexts[Math.floor(Math.random() * injuryGroupTexts.length)]
    );
    
    data.push({
      claim_id: `CLM-${1000 + i}`,
      VERSIONID: 100000 + Math.floor(Math.random() * 900000),
      claim_date: claimDate,
      DURATIONTOREPORT: Math.floor(Math.random() * 15),
      DOLLARAMOUNTHIGH: dollarAmountHigh,
      ALL_BODYPARTS: selectedBodyParts.join(', '),
      ALL_INJURIES: selectedInjuries.join(', '),
      ALL_INJURYGROUP_CODES: selectedGroupCodes.join(', '),
      ALL_INJURYGROUP_TEXTS: selectedGroupTexts.join(', '),
      PRIMARY_INJURY: selectedInjuries[0],
      PRIMARY_BODYPART: selectedBodyParts[0],
      PRIMARY_INJURYGROUP_CODE: selectedGroupCodes[0],
      INJURY_COUNT: injuryCount,
      BODYPART_COUNT: bodypartCount,
      INJURYGROUP_COUNT: injuryGroupCount,
      SETTLEMENT_DAYS: settlementDays,
      SETTLEMENT_MONTHS: settlementMonths,
      SETTLEMENT_YEARS: settlementYears,
      IMPACT: impact,
      COUNTYNAME: counties[countyIdx],
      VENUESTATE: states[countyIdx],
      VENUE_RATING: venueRating,
      RATINGWEIGHT: ratingWeight,
      INJURY_GROUP_CODE: selectedGroupCodes[0],
      CAUSATION__HIGH_RECOMMENDATION: causationHighRec,
      SEVERITY_SCORE: severityScore,
      CAUTION_LEVEL: cautionLevel,
      adjuster: adjusters[Math.floor(Math.random() * adjusters.length)],
      predicted_pain_suffering: predicted,
      variance_pct: variancePct,
      // Causation factors
      causation_probability: causationProbabilityWeights[Math.floor(Math.random() * causationProbabilityWeights.length)],
      causation_tx_delay: causationTxDelayWeights[Math.floor(Math.random() * causationTxDelayWeights.length)],
      causation_tx_gaps: causationTxGapsWeights[Math.floor(Math.random() * causationTxGapsWeights.length)],
      causation_compliance: causationComplianceWeights[Math.floor(Math.random() * causationComplianceWeights.length)],
      // Severity factors
      severity_allowed_tx_period: severityAllowedTxPeriodWeights[Math.floor(Math.random() * severityAllowedTxPeriodWeights.length)],
      severity_initial_tx: severityInitialTxWeights[Math.floor(Math.random() * severityInitialTxWeights.length)],
      severity_injections: severityInjectionsWeights[Math.floor(Math.random() * severityInjectionsWeights.length)],
      severity_objective_findings: severityObjectiveFindingsWeights[Math.floor(Math.random() * severityObjectiveFindingsWeights.length)],
      severity_pain_mgmt: severityPainMgmtWeights[Math.floor(Math.random() * severityPainMgmtWeights.length)],
      severity_type_tx: severityTypeTxWeights[Math.floor(Math.random() * severityTypeTxWeights.length)],
      severity_injury_site: severityInjurySiteWeights[Math.floor(Math.random() * severityInjurySiteWeights.length)],
      severity_code: severityCodeWeights[Math.floor(Math.random() * severityCodeWeights.length)]
    });
  }
  
  return data;
}
