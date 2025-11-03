import { ClaimData, WeightConfig, WeightAdjustment, RecalibrationResult, RecalibrationMetrics, WeightOptimizationRecommendation } from '../types/claims';

// List of all weight factors
export const WEIGHT_FACTORS = [
  'causation_probability',
  'causation_tx_delay',
  'causation_tx_gaps',
  'causation_compliance',
  'severity_allowed_tx_period',
  'severity_initial_tx',
  'severity_injections',
  'severity_objective_findings',
  'severity_pain_mgmt',
  'severity_type_tx',
  'severity_injury_site',
  'severity_code',
  'Advanced_Pain_Treatment',
  'Causation_Compliance',
  'Clinical_Findings',
  'Cognitive_Symptoms',
  'Complete_Disability_Duration',
  'Concussion_Diagnosis',
  'Consciousness_Impact',
  'Consistent_Mechanism',
  'Dental_Procedure',
  'Emergency_Treatment',
  'Fixation_Method',
  'Head_Trauma',
  'Immobilization_Used',
  'Injury_Count',
  'Injury_Extent',
  'Injury_Laterality',
  'Injury_Location',
  'Injury_Type',
  'Mobility_Assistance',
  'Movement_Restriction',
  'Nerve_Involvement',
  'Pain_Management',
  'Partial_Disability_Duration',
  'Physical_Symptoms',
  'Physical_Therapy',
  'Prior_Treatment',
  'Recovery_Duration',
  'Repair_Type',
  'Respiratory_Issues',
  'Soft_Tissue_Damage',
  'Special_Treatment',
  'Surgical_Intervention',
  'Symptom_Timeline',
  'Treatment_Compliance',
  'Treatment_Course',
  'Treatment_Delays',
  'Treatment_Level',
  'Treatment_Period_Considered',
  'Vehicle_Impact',
] as const;

/**
 * Convert categorical text values to numeric scores for calculation
 */
export function categoricalToNumeric(value: string | number | undefined): number {
  if (typeof value === 'number') return value;
  if (!value) return 0;

  const val = value.toLowerCase();

  // Yes/No mappings
  if (val === 'yes' || val === 'present') return 1;
  if (val === 'no' || val === 'absent') return 0;

  // Severity levels
  if (val.includes('severe') || val === 'high') return 1;
  if (val.includes('moderate') || val === 'medium') return 0.6;
  if (val.includes('mild') || val === 'low') return 0.3;

  // Duration mappings
  if (val.includes('more than 12 weeks') || val.includes('>12')) return 1;
  if (val.includes('5-12') || val.includes('5 - 12')) return 0.7;
  if (val.includes('2-4') || val.includes('2 - 4')) return 0.4;
  if (val.includes('less than') || val.includes('<')) return 0.2;

  // Treatment levels
  if (val.includes('invasive') || val.includes('surgical')) return 1;
  if (val.includes('non-invasive')) return 0.4;
  if (val.includes('passive')) return 0.3;
  if (val.includes('active')) return 0.6;

  // Compliance
  if (val.includes('compliant')) return 1;
  if (val.includes('non-compliant')) return 0.2;
  if (val.includes('partial')) return 0.5;

  // Emergency treatment
  if (val.includes('inpatient')) return 1;
  if (val.includes('outpatient')) return 0.6;
  if (val.includes('treated & released')) return 0.4;

  // Location mappings
  if (val.includes('bilateral')) return 1;
  if (val.includes('unilateral')) return 0.6;
  if (val.includes('multiple')) return 0.9;
  if (val.includes('single')) return 0.5;

  // Timing
  if (val.includes('immediate') || val.includes('first 48')) return 1;
  if (val.includes('more than 7')) return 0.3;

  // Mechanism consistency
  if (val.includes('consistent')) return 1;
  if (val.includes('inconsistent')) return 0.2;

  // Default: try to parse as number or return 0
  const parsed = parseFloat(val);
  return isNaN(parsed) ? 0 : Math.min(1, Math.max(0, parsed));
}

/**
 * Calculate weighted score for a claim using provided weights
 */
export function calculateWeightedScore(
  claim: ClaimData,
  weights: Map<string, number>
): number {
  let totalScore = 0;
  let totalWeight = 0;

  WEIGHT_FACTORS.forEach((factor) => {
    const weight = weights.get(factor) || 0;
    const value = claim[factor as keyof ClaimData];
    const numericValue = categoricalToNumeric(value);

    totalScore += numericValue * weight;
    totalWeight += weight;
  });

  // Normalize by total weight to get a score between 0 and 1
  return totalWeight > 0 ? totalScore / totalWeight : 0;
}

/**
 * Recalibrate a single claim prediction using adjusted weights
 */
export function recalibrateClaim(
  claim: ClaimData,
  originalWeights: Map<string, number>,
  adjustedWeights: Map<string, number>,
  baselinePrediction?: number
): RecalibrationResult {
  const originalScore = calculateWeightedScore(claim, originalWeights);
  const adjustedScore = calculateWeightedScore(claim, adjustedWeights);

  // Use existing prediction as baseline or calculate from original score
  const originalPrediction = baselinePrediction || claim.predicted_pain_suffering;
  const actualValue = claim.DOLLARAMOUNTHIGH;

  // Apply the score differential to the prediction
  const scoreDiff = adjustedScore - originalScore;
  const recalibratedPrediction = originalPrediction * (1 + scoreDiff);

  // Calculate variance percentages
  const originalVariancePct = Math.abs((originalPrediction - actualValue) / actualValue * 100);
  const recalibratedVariancePct = Math.abs((recalibratedPrediction - actualValue) / actualValue * 100);

  // Calculate improvement
  const improvementPct = ((originalVariancePct - recalibratedVariancePct) / originalVariancePct * 100);

  return {
    claim_id: claim.claim_id,
    original_prediction: originalPrediction,
    recalibrated_prediction: recalibratedPrediction,
    actual_value: actualValue,
    original_variance_pct: originalVariancePct,
    recalibrated_variance_pct: recalibratedVariancePct,
    improvement_pct: improvementPct,
  };
}

/**
 * Recalibrate all claims and generate metrics
 */
export function recalibrateAllClaims(
  claims: ClaimData[],
  originalWeights: Map<string, number>,
  adjustedWeights: Map<string, number>
): { results: RecalibrationResult[]; metrics: RecalibrationMetrics } {
  const results = claims.map((claim) =>
    recalibrateClaim(claim, originalWeights, adjustedWeights)
  );

  // Calculate aggregate metrics
  const improved = results.filter((r) => r.improvement_pct > 1); // >1% improvement
  const degraded = results.filter((r) => r.improvement_pct < -1); // >1% degradation
  const unchanged = results.filter((r) => Math.abs(r.improvement_pct) <= 1);

  const avgImprovement = results.reduce((sum, r) => sum + r.improvement_pct, 0) / results.length;

  // Calculate MAPE (Mean Absolute Percentage Error)
  const mapeBefore = results.reduce((sum, r) => sum + r.original_variance_pct, 0) / results.length;
  const mapeAfter = results.reduce((sum, r) => sum + r.recalibrated_variance_pct, 0) / results.length;

  // Calculate RMSE (Root Mean Square Error)
  const rmseBefore = Math.sqrt(
    results.reduce((sum, r) => sum + Math.pow(r.original_prediction - r.actual_value, 2), 0) / results.length
  );
  const rmseAfter = Math.sqrt(
    results.reduce((sum, r) => sum + Math.pow(r.recalibrated_prediction - r.actual_value, 2), 0) / results.length
  );

  const metrics: RecalibrationMetrics = {
    total_claims: results.length,
    improved_count: improved.length,
    degraded_count: degraded.length,
    unchanged_count: unchanged.length,
    avg_improvement_pct: avgImprovement,
    mape_before: mapeBefore,
    mape_after: mapeAfter,
    rmse_before: rmseBefore,
    rmse_after: rmseAfter,
  };

  return { results, metrics };
}

/**
 * Calculate factor impact - how much each factor contributes to variance
 */
export function calculateFactorImpact(
  claims: ClaimData[],
  weights: Map<string, number>
): Map<string, number> {
  const factorImpacts = new Map<string, number>();

  WEIGHT_FACTORS.forEach((factor) => {
    let totalImpact = 0;

    claims.forEach((claim) => {
      const value = categoricalToNumeric(claim[factor as keyof ClaimData]);
      const weight = weights.get(factor) || 0;
      const variancePct = Math.abs(claim.variance_pct);

      // Impact is correlation between weighted value and variance
      totalImpact += value * weight * variancePct;
    });

    factorImpacts.set(factor, totalImpact / claims.length);
  });

  return factorImpacts;
}

/**
 * Calculate correlation between a factor and variance (used for dynamic recommendations)
 */
export function calculateFactorCorrelation(
  claims: ClaimData[],
  factorName: string
): number {
  const values: number[] = [];
  const variances: number[] = [];

  claims.forEach((claim) => {
    const value = claim[factorName as keyof ClaimData];
    const numericValue = categoricalToNumeric(value);
    if (!isNaN(numericValue)) {
      values.push(numericValue);
      variances.push(Math.abs(claim.variance_pct));
    }
  });

  if (values.length < 2) return 0;

  // Calculate Pearson correlation coefficient
  const n = values.length;
  const meanValue = values.reduce((a, b) => a + b, 0) / n;
  const meanVariance = variances.reduce((a, b) => a + b, 0) / n;

  let numerator = 0;
  let denomValue = 0;
  let denomVariance = 0;

  for (let i = 0; i < n; i++) {
    const diffValue = values[i] - meanValue;
    const diffVariance = variances[i] - meanVariance;
    numerator += diffValue * diffVariance;
    denomValue += diffValue * diffValue;
    denomVariance += diffVariance * diffVariance;
  }

  const denominator = Math.sqrt(denomValue * denomVariance);
  return denominator === 0 ? 0 : numerator / denominator;
}

/**
 * Generate optimization recommendations based on current performance
 * DYNAMIC VERSION - calculates recommended weights based on data
 */
export function generateOptimizationRecommendations(
  claims: ClaimData[],
  currentWeights: WeightConfig[],
  factorImpacts: Map<string, number>
): WeightOptimizationRecommendation[] {
  const recommendations: WeightOptimizationRecommendation[] = [];

  // Find max impact for normalization
  const maxImpact = Math.max(...Array.from(factorImpacts.values()));

  currentWeights.forEach((weightConfig) => {
    const currentWeight = weightConfig.base_weight;
    const impact = factorImpacts.get(weightConfig.factor_name) || 0;
    const normalizedImpact = maxImpact > 0 ? impact / maxImpact : 0;

    // Calculate correlation with variance
    const correlation = Math.abs(calculateFactorCorrelation(claims, weightConfig.factor_name));

    // Calculate DYNAMIC recommended weight based on correlation and impact
    const correlationScore = correlation; // 0 to 1
    const impactScore = normalizedImpact; // 0 to 1

    // Combined score (weighted average)
    const combinedScore = correlationScore * 0.6 + impactScore * 0.4;

    // Map combined score to weight range
    const weightRange = weightConfig.max_weight - weightConfig.min_weight;
    const dynamicRecommended = weightConfig.min_weight + combinedScore * weightRange;

    // Analyze if weight should be adjusted
    let suggestedWeight = dynamicRecommended;
    let reason = '';
    let confidence: 'high' | 'medium' | 'low' = 'medium';
    let expectedImprovement = 0;

    // High correlation and high impact = definitely increase
    if (correlation > 0.5 && normalizedImpact > 0.6 && currentWeight < dynamicRecommended) {
      suggestedWeight = Math.min(weightConfig.max_weight, dynamicRecommended);
      reason = `High correlation (${(correlation * 100).toFixed(1)}%) and high impact (${impact.toFixed(2)}). Increasing weight will likely improve predictions.`;
      confidence = 'high';
      expectedImprovement = Math.round(correlation * 10);
    }
    // High impact but weight is too low
    else if (normalizedImpact > 0.5 && currentWeight < dynamicRecommended * 0.8) {
      suggestedWeight = Math.min(weightConfig.max_weight, dynamicRecommended);
      reason = `Factor has high impact (${impact.toFixed(2)}) but is underweighted. Dynamic analysis suggests increasing to ${suggestedWeight.toFixed(3)}.`;
      confidence = 'high';
      expectedImprovement = Math.round(normalizedImpact * 8);
    }
    // Low impact and overweighted
    else if (normalizedImpact < 0.3 && currentWeight > dynamicRecommended * 1.2) {
      suggestedWeight = Math.max(weightConfig.min_weight, dynamicRecommended);
      reason = `Low impact factor (${impact.toFixed(2)}) is overweighted. Reducing weight may improve efficiency without hurting accuracy.`;
      confidence = 'medium';
      expectedImprovement = Math.round((currentWeight - suggestedWeight) * 20);
    }
    // Moderate deviation from dynamic recommendation
    else if (Math.abs(currentWeight - dynamicRecommended) > 0.02) {
      suggestedWeight = dynamicRecommended;
      reason = `Data-driven analysis suggests optimal weight is ${dynamicRecommended.toFixed(3)} (correlation: ${(correlation * 100).toFixed(1)}%, impact: ${normalizedImpact.toFixed(2)}).`;
      confidence = 'medium';
      expectedImprovement = Math.round(Math.abs(currentWeight - dynamicRecommended) * 30);
    }
    // Performing well
    else {
      reason = `Weight is near optimal (current: ${currentWeight.toFixed(3)}, recommended: ${dynamicRecommended.toFixed(3)}).`;
      confidence = 'low';
      expectedImprovement = 0;
    }

    // Only add if there's a meaningful suggestion
    if (Math.abs(suggestedWeight - currentWeight) > 0.01) {
      recommendations.push({
        factor_name: weightConfig.factor_name,
        current_weight: currentWeight,
        suggested_weight: suggestedWeight,
        reason,
        expected_improvement: expectedImprovement,
        confidence,
      });
    }
  });

  // Sort by expected improvement
  return recommendations.sort((a, b) => b.expected_improvement - a.expected_improvement);
}

/**
 * Perform sensitivity analysis - test impact of adjusting single weight
 */
export function performSensitivityAnalysis(
  claims: ClaimData[],
  baseWeights: Map<string, number>,
  factorName: string,
  testWeights: number[]
): { weight: number; mape: number; rmse: number }[] {
  const results = testWeights.map((testWeight) => {
    const adjustedWeights = new Map(baseWeights);
    adjustedWeights.set(factorName, testWeight);

    const { metrics } = recalibrateAllClaims(claims, baseWeights, adjustedWeights);

    return {
      weight: testWeight,
      mape: metrics.mape_after,
      rmse: metrics.rmse_after,
    };
  });

  return results;
}

/**
 * Export weights to CSV format
 */
export function exportWeightsToCSV(weights: WeightConfig[], adjustments?: Map<string, number>): string {
  const headers = 'factor_name,base_weight,min_weight,max_weight,recommended_weight,adjusted_weight,category,description\n';

  const rows = weights.map((w) => {
    const adjustedWeight = adjustments?.get(w.factor_name) || w.base_weight;
    return `${w.factor_name},${w.base_weight},${w.min_weight},${w.max_weight},${w.recommended_weight},${adjustedWeight},${w.category},"${w.description}"`;
  }).join('\n');

  return headers + rows;
}
