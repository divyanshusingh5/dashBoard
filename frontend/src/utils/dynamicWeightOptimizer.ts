import { ClaimData, WeightConfig } from '../types/claims';
import { WEIGHT_FACTORS, calculateWeightedScore, recalibrateAllClaims } from './recalibrationEngine';

export interface OptimizationConfig {
  targetMetric: 'mape' | 'rmse' | 'both';
  maxIterations: number;
  learningRate: number;
  convergenceThreshold: number;
  keepFactorsConstant?: string[]; // Factors to exclude from optimization
}

export interface OptimizationResult {
  optimizedWeights: Map<string, number>;
  iterations: number;
  finalMAPE: number;
  finalRMSE: number;
  improvementPct: number;
  convergenceHistory: {
    iteration: number;
    mape: number;
    rmse: number;
    weightChanges: Map<string, number>;
  }[];
}

/**
 * Calculate correlation between a factor and variance
 * This helps identify which factors are most predictive
 */
export function calculateFactorCorrelation(
  claims: ClaimData[],
  factorName: string
): number {
  const values: number[] = [];
  const variances: number[] = [];

  claims.forEach((claim) => {
    const value = claim[factorName as keyof ClaimData];
    if (typeof value === 'number' && !isNaN(value)) {
      values.push(value);
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
 * Calculate recommended weight based on factor correlation and impact
 */
export function calculateDynamicRecommendedWeight(
  claims: ClaimData[],
  weightConfig: WeightConfig,
  currentWeights: Map<string, number>,
  factorImpacts: Map<string, number>
): number {
  const { factor_name, base_weight, min_weight, max_weight } = weightConfig;

  // Get correlation with variance
  const correlation = Math.abs(calculateFactorCorrelation(claims, factor_name));

  // Get current impact
  const impact = factorImpacts.get(factor_name) || 0;
  const maxImpact = Math.max(...Array.from(factorImpacts.values()));
  const normalizedImpact = maxImpact > 0 ? impact / maxImpact : 0;

  // Calculate recommended weight based on correlation and impact
  // High correlation and high impact = higher weight
  const correlationScore = correlation; // 0 to 1
  const impactScore = normalizedImpact; // 0 to 1

  // Combined score (weighted average)
  const combinedScore = correlationScore * 0.6 + impactScore * 0.4;

  // Map combined score to weight range
  const weightRange = max_weight - min_weight;
  const recommendedWeight = min_weight + combinedScore * weightRange;

  // Ensure within bounds
  return Math.max(min_weight, Math.min(max_weight, recommendedWeight));
}

/**
 * Calculate optimal weights for all factors dynamically
 */
export function calculateOptimalWeights(
  claims: ClaimData[],
  weights: WeightConfig[],
  factorImpacts: Map<string, number>
): Map<string, number> {
  const optimalWeights = new Map<string, number>();
  const currentWeights = new Map<string, number>();

  // Initialize with base weights
  weights.forEach((w) => currentWeights.set(w.factor_name, w.base_weight));

  // Calculate optimal weight for each factor
  weights.forEach((weightConfig) => {
    const recommended = calculateDynamicRecommendedWeight(
      claims,
      weightConfig,
      currentWeights,
      factorImpacts
    );
    optimalWeights.set(weightConfig.factor_name, recommended);
  });

  // Normalize weights to maintain relative scale
  const totalOptimal = Array.from(optimalWeights.values()).reduce((a, b) => a + b, 0);
  const totalBase = Array.from(currentWeights.values()).reduce((a, b) => a + b, 0);
  const normalizationFactor = totalBase / totalOptimal;

  optimalWeights.forEach((weight, factor) => {
    optimalWeights.set(factor, weight * normalizationFactor);
  });

  return optimalWeights;
}

/**
 * Gradient descent optimization for finding best weights
 * Keeps specified factors constant while optimizing others
 */
export function optimizeWeightsGradientDescent(
  claims: ClaimData[],
  weights: WeightConfig[],
  config: OptimizationConfig
): OptimizationResult {
  const {
    targetMetric,
    maxIterations,
    learningRate,
    convergenceThreshold,
    keepFactorsConstant = [],
  } = config;

  // Initialize weights
  const currentWeights = new Map<string, number>();
  const factorsToOptimize = new Set<string>();

  weights.forEach((w) => {
    currentWeights.set(w.factor_name, w.base_weight);
    if (!keepFactorsConstant.includes(w.factor_name)) {
      factorsToOptimize.add(w.factor_name);
    }
  });

  const weightsMap = new Map<string, WeightConfig>();
  weights.forEach((w) => weightsMap.set(w.factor_name, w));

  // Track convergence history
  const convergenceHistory: OptimizationResult['convergenceHistory'] = [];

  // Calculate initial metrics
  const initialResults = recalibrateAllClaims(claims, currentWeights, currentWeights);
  let bestMAPE = initialResults.metrics.mape_after;
  let bestRMSE = initialResults.metrics.rmse_after;
  let bestWeights = new Map(currentWeights);

  let iteration = 0;
  let converged = false;

  while (iteration < maxIterations && !converged) {
    iteration++;
    const weightChanges = new Map<string, number>();

    // For each factor that we're optimizing
    for (const factor of factorsToOptimize) {
      const weightConfig = weightsMap.get(factor)!;
      const currentWeight = currentWeights.get(factor)!;

      // Try small positive and negative changes
      const delta = learningRate * (weightConfig.max_weight - weightConfig.min_weight);

      // Test positive change
      const testWeightsPos = new Map(currentWeights);
      testWeightsPos.set(factor, Math.min(weightConfig.max_weight, currentWeight + delta));

      // Test negative change
      const testWeightsNeg = new Map(currentWeights);
      testWeightsNeg.set(factor, Math.max(weightConfig.min_weight, currentWeight - delta));

      // Evaluate both
      const resultsPos = recalibrateAllClaims(claims, currentWeights, testWeightsPos);
      const resultsNeg = recalibrateAllClaims(claims, currentWeights, testWeightsNeg);

      const currentMetricPos = targetMetric === 'mape' ? resultsPos.metrics.mape_after :
                               targetMetric === 'rmse' ? resultsPos.metrics.rmse_after :
                               (resultsPos.metrics.mape_after + resultsPos.metrics.rmse_after / 10000);

      const currentMetricNeg = targetMetric === 'mape' ? resultsNeg.metrics.mape_after :
                               targetMetric === 'rmse' ? resultsNeg.metrics.rmse_after :
                               (resultsNeg.metrics.mape_after + resultsNeg.metrics.rmse_after / 10000);

      const currentMetric = targetMetric === 'mape' ? bestMAPE :
                            targetMetric === 'rmse' ? bestRMSE :
                            (bestMAPE + bestRMSE / 10000);

      // Move in direction of improvement
      if (currentMetricPos < currentMetric) {
        const newWeight = Math.min(weightConfig.max_weight, currentWeight + delta);
        currentWeights.set(factor, newWeight);
        weightChanges.set(factor, newWeight - currentWeight);
        bestMAPE = resultsPos.metrics.mape_after;
        bestRMSE = resultsPos.metrics.rmse_after;
        bestWeights = new Map(testWeightsPos);
      } else if (currentMetricNeg < currentMetric) {
        const newWeight = Math.max(weightConfig.min_weight, currentWeight - delta);
        currentWeights.set(factor, newWeight);
        weightChanges.set(factor, newWeight - currentWeight);
        bestMAPE = resultsNeg.metrics.mape_after;
        bestRMSE = resultsNeg.metrics.rmse_after;
        bestWeights = new Map(testWeightsNeg);
      }
    }

    // Record history
    convergenceHistory.push({
      iteration,
      mape: bestMAPE,
      rmse: bestRMSE,
      weightChanges: new Map(weightChanges),
    });

    // Check convergence - if no weights changed significantly
    const maxWeightChange = Math.max(...Array.from(weightChanges.values()).map(Math.abs), 0);
    if (maxWeightChange < convergenceThreshold) {
      converged = true;
    }
  }

  const finalResults = recalibrateAllClaims(claims, currentWeights, bestWeights);
  const improvementPct = ((initialResults.metrics.mape_after - finalResults.metrics.mape_after) /
                          initialResults.metrics.mape_after) * 100;

  return {
    optimizedWeights: bestWeights,
    iterations: iteration,
    finalMAPE: bestMAPE,
    finalRMSE: bestRMSE,
    improvementPct,
    convergenceHistory,
  };
}

/**
 * Grid search optimization - tests different weight combinations
 * Keeps specified factors constant
 */
export function optimizeWeightsGridSearch(
  claims: ClaimData[],
  weights: WeightConfig[],
  config: OptimizationConfig & { gridSteps?: number }
): OptimizationResult {
  const {
    targetMetric,
    keepFactorsConstant = [],
    gridSteps = 5,
  } = config;

  // Identify factors to optimize
  const factorsToOptimize = weights.filter(
    (w) => !keepFactorsConstant.includes(w.factor_name)
  );

  // Initialize with base weights
  const baseWeights = new Map<string, number>();
  weights.forEach((w) => baseWeights.set(w.factor_name, w.base_weight));

  let bestWeights = new Map(baseWeights);
  let bestMetric = Infinity;
  let bestMAPE = 0;
  let bestRMSE = 0;
  const convergenceHistory: OptimizationResult['convergenceHistory'] = [];

  // For smaller optimization sets, try focused grid search
  // We'll optimize one factor at a time to avoid combinatorial explosion
  let iteration = 0;

  for (const weightConfig of factorsToOptimize) {
    const step = (weightConfig.max_weight - weightConfig.min_weight) / gridSteps;

    for (let i = 0; i <= gridSteps; i++) {
      iteration++;
      const testWeight = weightConfig.min_weight + step * i;
      const testWeights = new Map(bestWeights);
      testWeights.set(weightConfig.factor_name, testWeight);

      const results = recalibrateAllClaims(claims, baseWeights, testWeights);

      const metric = targetMetric === 'mape' ? results.metrics.mape_after :
                     targetMetric === 'rmse' ? results.metrics.rmse_after :
                     (results.metrics.mape_after + results.metrics.rmse_after / 10000);

      if (metric < bestMetric) {
        bestMetric = metric;
        bestWeights = new Map(testWeights);
        bestMAPE = results.metrics.mape_after;
        bestRMSE = results.metrics.rmse_after;

        convergenceHistory.push({
          iteration,
          mape: bestMAPE,
          rmse: bestRMSE,
          weightChanges: new Map([[weightConfig.factor_name, testWeight - weightConfig.base_weight]]),
        });
      }
    }
  }

  const initialResults = recalibrateAllClaims(claims, baseWeights, baseWeights);
  const improvementPct = ((initialResults.metrics.mape_after - bestMAPE) /
                          initialResults.metrics.mape_after) * 100;

  return {
    optimizedWeights: bestWeights,
    iterations: iteration,
    finalMAPE: bestMAPE,
    finalRMSE: bestRMSE,
    improvementPct,
    convergenceHistory,
  };
}

/**
 * Smart optimization that uses correlation analysis to prioritize factors
 * Then applies focused optimization to high-impact factors
 */
export function optimizeWeightsSmart(
  claims: ClaimData[],
  weights: WeightConfig[],
  factorImpacts: Map<string, number>,
  config: OptimizationConfig
): OptimizationResult {
  const { keepFactorsConstant = [] } = config;

  // Calculate correlations for all factors
  const factorScores = new Map<string, number>();

  weights.forEach((weightConfig) => {
    if (keepFactorsConstant.includes(weightConfig.factor_name)) {
      factorScores.set(weightConfig.factor_name, 0);
      return;
    }

    const correlation = Math.abs(calculateFactorCorrelation(claims, weightConfig.factor_name));
    const impact = factorImpacts.get(weightConfig.factor_name) || 0;
    const maxImpact = Math.max(...Array.from(factorImpacts.values()));
    const normalizedImpact = maxImpact > 0 ? impact / maxImpact : 0;

    // Combined score
    const score = correlation * 0.5 + normalizedImpact * 0.5;
    factorScores.set(weightConfig.factor_name, score);
  });

  // Sort factors by score
  const sortedFactors = Array.from(factorScores.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([factor]) => factor);

  // Optimize top factors only (top 10)
  const topFactors = sortedFactors.slice(0, Math.min(10, sortedFactors.length));

  // Run gradient descent on top factors
  const optimizationResult = optimizeWeightsGradientDescent(
    claims,
    weights,
    {
      ...config,
      keepFactorsConstant: [
        ...keepFactorsConstant,
        ...sortedFactors.filter((f) => !topFactors.includes(f)),
      ],
    }
  );

  return optimizationResult;
}
