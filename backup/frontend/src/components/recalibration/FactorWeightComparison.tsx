import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { TrendingUp, TrendingDown, Minus, ArrowRight } from 'lucide-react';
import { ClaimData } from '../../types/claims';

interface FactorWeightComparisonProps {
  claims: ClaimData[];
  coefficients: {
    C0: number;
    C1: number;
    C2: number;
    C3: number;
    C4: number;
    C5: number;
    C6: number;
  };
  defaultCoefficients: {
    C0: number;
    C1: number;
    C2: number;
    C3: number;
    C4: number;
    C5: number;
    C6: number;
  };
}

interface FactorAnalysis {
  factor_name: string;
  category: 'Severity' | 'Causation';
  current_avg_value: number;
  current_contribution: number;
  suggested_contribution: number;
  impact_on_prediction: number;
  impact_pct: number;
  change_direction: 'increase' | 'decrease' | 'stable';
}

export default function FactorWeightComparison({
  claims,
  coefficients,
  defaultCoefficients,
}: FactorWeightComparisonProps) {

  // Calculate severity sum for a claim
  const calculateSeveritySum = (claim: ClaimData): number => {
    let sum = 0;
    const severityFactors = [
      'severity_allowed_tx_period',
      'severity_initial_tx',
      'severity_injections',
      'severity_objective_findings',
      'severity_pain_mgmt',
      'severity_type_tx',
      'severity_injury_site',
      'severity_code',
    ];

    severityFactors.forEach(factor => {
      const value = claim[factor as keyof ClaimData];
      if (typeof value === 'number') {
        sum += value;
      } else if (typeof value === 'string') {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) sum += numValue;
      }
    });

    if (claim.SEVERITY_SCORE) {
      sum += parseFloat(String(claim.SEVERITY_SCORE));
    }

    return sum;
  };

  // Calculate causation sum for a claim
  const calculateCausationSum = (claim: ClaimData): number => {
    let sum = 0;
    const causationFactors = [
      'causation_probability',
      'causation_tx_delay',
      'causation_tx_gaps',
      'causation_compliance',
    ];

    causationFactors.forEach(factor => {
      const value = claim[factor as keyof ClaimData];
      if (typeof value === 'number') {
        sum += value;
      } else if (typeof value === 'string') {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) sum += numValue;
      }
    });

    return sum;
  };

  // Get impact score
  const getImpactScore = (claim: ClaimData): number => {
    if (claim.IMPACT) {
      const impact = typeof claim.IMPACT === 'number' ? claim.IMPACT : parseInt(String(claim.IMPACT));
      return Math.min(4, Math.max(1, impact));
    }
    return 2;
  };

  // Analyze individual severity factors
  const severityFactorAnalysis = useMemo((): FactorAnalysis[] => {
    const severityFactors = [
      { key: 'severity_allowed_tx_period', name: 'Allowed Treatment Period' },
      { key: 'severity_initial_tx', name: 'Initial Treatment' },
      { key: 'severity_injections', name: 'Injections' },
      { key: 'severity_objective_findings', name: 'Objective Findings' },
      { key: 'severity_pain_mgmt', name: 'Pain Management' },
      { key: 'severity_type_tx', name: 'Type of Treatment' },
      { key: 'severity_injury_site', name: 'Injury Site' },
      { key: 'severity_code', name: 'Severity Code' },
    ];

    return severityFactors.map(factor => {
      // Calculate average value for this factor across all claims
      let sum = 0;
      let count = 0;
      claims.forEach(claim => {
        const value = claim[factor.key as keyof ClaimData];
        if (typeof value === 'number' && value > 0) {
          sum += value;
          count++;
        } else if (typeof value === 'string') {
          const numValue = parseFloat(value);
          if (!isNaN(numValue) && numValue > 0) {
            sum += numValue;
            count++;
          }
        }
      });

      const avgValue = count > 0 ? sum / count : 0;

      // Calculate average severity sum and impact for context
      const avgSeveritySum = claims.reduce((acc, c) => acc + calculateSeveritySum(c), 0) / claims.length;
      const avgImpact = claims.reduce((acc, c) => acc + getImpactScore(c), 0) / claims.length;

      // Current contribution to exponent: C1*S + C6*S²
      const currentLinearContribution = defaultCoefficients.C1 * avgValue;
      const currentQuadraticContribution = defaultCoefficients.C6 * Math.pow(avgValue, 2);
      const currentTotalContribution = currentLinearContribution + currentQuadraticContribution;

      // Suggested contribution with new coefficients
      const suggestedLinearContribution = coefficients.C1 * avgValue;
      const suggestedQuadraticContribution = coefficients.C6 * Math.pow(avgValue, 2);
      const suggestedTotalContribution = suggestedLinearContribution + suggestedQuadraticContribution;

      // Impact on final prediction (exponential effect)
      const contributionDelta = suggestedTotalContribution - currentTotalContribution;
      const avgBasePrediction = 100000; // Approximate base
      const impactOnPrediction = avgBasePrediction * (Math.exp(suggestedTotalContribution) - Math.exp(currentTotalContribution));
      const impactPct = (contributionDelta / currentTotalContribution) * 100;

      let changeDirection: 'increase' | 'decrease' | 'stable' = 'stable';
      if (Math.abs(impactPct) > 5) {
        changeDirection = impactPct > 0 ? 'increase' : 'decrease';
      }

      return {
        factor_name: factor.name,
        category: 'Severity' as const,
        current_avg_value: avgValue,
        current_contribution: currentTotalContribution,
        suggested_contribution: suggestedTotalContribution,
        impact_on_prediction: impactOnPrediction,
        impact_pct: impactPct,
        change_direction: changeDirection,
      };
    });
  }, [claims, coefficients, defaultCoefficients]);

  // Analyze individual causation factors
  const causationFactorAnalysis = useMemo((): FactorAnalysis[] => {
    const causationFactors = [
      { key: 'causation_probability', name: 'Causation Probability' },
      { key: 'causation_tx_delay', name: 'Treatment Delay' },
      { key: 'causation_tx_gaps', name: 'Treatment Gaps' },
      { key: 'causation_compliance', name: 'Compliance' },
    ];

    return causationFactors.map(factor => {
      // Calculate average value for this factor across all claims
      let sum = 0;
      let count = 0;
      claims.forEach(claim => {
        const value = claim[factor.key as keyof ClaimData];
        if (typeof value === 'number' && value > 0) {
          sum += value;
          count++;
        } else if (typeof value === 'string') {
          const numValue = parseFloat(value);
          if (!isNaN(numValue) && numValue > 0) {
            sum += numValue;
            count++;
          }
        }
      });

      const avgValue = count > 0 ? sum / count : 0;

      // Causation affects as multiplier: (1 + 0.1 * CausationSum)
      const avgCausationSum = claims.reduce((acc, c) => acc + calculateCausationSum(c), 0) / claims.length;

      // Current and suggested multipliers
      const currentMultiplier = 1 + (0.1 * avgValue);
      const suggestedMultiplier = currentMultiplier; // Causation multiplier is fixed at 0.1, but value matters

      // Impact if this factor increases by 10%
      const increasedValue = avgValue * 1.1;
      const increasedMultiplier = 1 + (0.1 * increasedValue);

      const avgBasePrediction = 100000;
      const currentPrediction = avgBasePrediction * currentMultiplier;
      const increasedPrediction = avgBasePrediction * increasedMultiplier;
      const impactOnPrediction = increasedPrediction - currentPrediction;
      const impactPct = ((increasedMultiplier - currentMultiplier) / currentMultiplier) * 100;

      return {
        factor_name: factor.name,
        category: 'Causation' as const,
        current_avg_value: avgValue,
        current_contribution: currentMultiplier,
        suggested_contribution: suggestedMultiplier,
        impact_on_prediction: impactOnPrediction,
        impact_pct: impactPct,
        change_direction: 'stable' as const, // Causation multiplier is fixed
      };
    });
  }, [claims]);

  // Combined coefficient impact summary
  const coefficientImpactSummary = useMemo(() => {
    const summary = [];

    // C1 - Severity Linear
    const c1Delta = coefficients.C1 - defaultCoefficients.C1;
    if (Math.abs(c1Delta) > 0.001) {
      summary.push({
        coefficient: 'C1 (Severity Linear)',
        current: defaultCoefficients.C1,
        suggested: coefficients.C1,
        change: c1Delta,
        impact: c1Delta > 0 ? 'Severity factors have MORE influence' : 'Severity factors have LESS influence',
      });
    }

    // C2 - Impact Linear
    const c2Delta = coefficients.C2 - defaultCoefficients.C2;
    if (Math.abs(c2Delta) > 0.001) {
      summary.push({
        coefficient: 'C2 (Impact Linear)',
        current: defaultCoefficients.C2,
        suggested: coefficients.C2,
        change: c2Delta,
        impact: c2Delta > 0 ? 'Impact score has MORE influence' : 'Impact score has LESS influence',
      });
    }

    // C3 - Interaction
    const c3Delta = coefficients.C3 - defaultCoefficients.C3;
    if (Math.abs(c3Delta) > 0.001) {
      summary.push({
        coefficient: 'C3 (Severity × Impact)',
        current: defaultCoefficients.C3,
        suggested: coefficients.C3,
        change: c3Delta,
        impact: c3Delta > 0 ? 'Combined severity+impact effect is STRONGER' : 'Combined severity+impact effect is WEAKER',
      });
    }

    // C6 - Severity Quadratic
    const c6Delta = coefficients.C6 - defaultCoefficients.C6;
    if (Math.abs(c6Delta) > 0.001) {
      summary.push({
        coefficient: 'C6 (Severity Quadratic)',
        current: defaultCoefficients.C6,
        suggested: coefficients.C6,
        change: c6Delta,
        impact: c6Delta < 0 ? 'MORE diminishing returns for high severity' : 'LESS diminishing returns for high severity',
      });
    }

    return summary;
  }, [coefficients, defaultCoefficients]);

  return (
    <div className="space-y-6">
      {/* Coefficient Impact Summary */}
      {coefficientImpactSummary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Coefficient Changes Impact</CardTitle>
            <CardDescription>
              How your coefficient adjustments affect the model
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {coefficientImpactSummary.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{item.coefficient}</div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                      <span>{item.current.toFixed(3)}</span>
                      <ArrowRight className="h-3 w-3" />
                      <span className="font-medium text-foreground">{item.suggested.toFixed(3)}</span>
                      <Badge variant={item.change > 0 ? 'default' : 'secondary'} className="ml-2">
                        {item.change > 0 ? '+' : ''}{item.change.toFixed(3)}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-sm text-right max-w-xs">
                    {item.impact}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Severity Factors Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Severity Factors Weight Analysis</CardTitle>
          <CardDescription>
            Individual severity factors and their contribution to predictions (affected by C1 and C6)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Factor</th>
                  <th className="text-right p-3">Avg Value</th>
                  <th className="text-right p-3">Current Contribution</th>
                  <th className="text-right p-3">New Contribution</th>
                  <th className="text-right p-3">Impact</th>
                  <th className="text-center p-3">Direction</th>
                </tr>
              </thead>
              <tbody>
                {severityFactorAnalysis
                  .sort((a, b) => Math.abs(b.impact_pct) - Math.abs(a.impact_pct))
                  .map((factor, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-medium">{factor.factor_name}</td>
                      <td className="p-3 text-right">{factor.current_avg_value.toFixed(3)}</td>
                      <td className="p-3 text-right font-mono">{factor.current_contribution.toFixed(4)}</td>
                      <td className="p-3 text-right font-mono font-semibold">
                        {factor.suggested_contribution.toFixed(4)}
                      </td>
                      <td className="p-3 text-right">
                        {Math.abs(factor.impact_pct) > 1 && (
                          <span className={factor.impact_pct > 0 ? 'text-green-600' : 'text-red-600'}>
                            {factor.impact_pct > 0 ? '+' : ''}{factor.impact_pct.toFixed(1)}%
                          </span>
                        )}
                        {Math.abs(factor.impact_pct) <= 1 && (
                          <span className="text-gray-400">
                            ~0%
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-center">
                        {factor.change_direction === 'increase' && (
                          <TrendingUp className="h-4 w-4 text-green-600 inline" />
                        )}
                        {factor.change_direction === 'decrease' && (
                          <TrendingDown className="h-4 w-4 text-red-600 inline" />
                        )}
                        {factor.change_direction === 'stable' && (
                          <Minus className="h-4 w-4 text-gray-400 inline" />
                        )}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
            <div className="font-semibold text-blue-900 mb-1">Understanding Severity Contributions:</div>
            <ul className="text-blue-800 space-y-1 ml-4 list-disc">
              <li><strong>Avg Value:</strong> Average value of this factor across all claims</li>
              <li><strong>Current Contribution:</strong> How much this factor contributes to exponent with baseline coefficients (C1×value + C6×value²)</li>
              <li><strong>New Contribution:</strong> How much with your adjusted coefficients</li>
              <li><strong>Impact:</strong> Percentage change in contribution (positive = more influential)</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Causation Factors Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Causation Factors Analysis</CardTitle>
          <CardDescription>
            Individual causation factors and their multiplier effect (fixed at 0.1× factor value)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Factor</th>
                  <th className="text-right p-3">Avg Value</th>
                  <th className="text-right p-3">Current Multiplier</th>
                  <th className="text-right p-3">Impact if +10%</th>
                </tr>
              </thead>
              <tbody>
                {causationFactorAnalysis
                  .sort((a, b) => b.current_avg_value - a.current_avg_value)
                  .map((factor, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-medium">{factor.factor_name}</td>
                      <td className="p-3 text-right">{factor.current_avg_value.toFixed(3)}</td>
                      <td className="p-3 text-right font-mono">{factor.current_contribution.toFixed(4)}×</td>
                      <td className="p-3 text-right text-green-600">
                        +${(factor.impact_on_prediction / 1000).toFixed(1)}K
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm">
            <div className="font-semibold text-amber-900 mb-1">Understanding Causation Impact:</div>
            <ul className="text-amber-800 space-y-1 ml-4 list-disc">
              <li><strong>Avg Value:</strong> Average value of this factor across all claims</li>
              <li><strong>Current Multiplier:</strong> Prediction multiplier: (1 + 0.1 × value)</li>
              <li><strong>Impact if +10%:</strong> How much predictions would increase if this factor's value increased by 10%</li>
              <li><strong>Note:</strong> Causation multiplier coefficient (0.1) is fixed in the equation</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Practical Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
          <CardDescription>
            What these factors tell you about your model
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* Top influential severity factor */}
            {severityFactorAnalysis.length > 0 && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="font-semibold text-green-900 mb-1">
                  Most Influential Severity Factor
                </div>
                <div className="text-sm text-green-800">
                  <strong>{severityFactorAnalysis.sort((a, b) => b.current_avg_value - a.current_avg_value)[0].factor_name}</strong>
                  {' '}has the highest average value ({severityFactorAnalysis.sort((a, b) => b.current_avg_value - a.current_avg_value)[0].current_avg_value.toFixed(3)}).
                  This factor has the most weight in determining severity scores.
                </div>
              </div>
            )}

            {/* Top influential causation factor */}
            {causationFactorAnalysis.length > 0 && (
              <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="font-semibold text-purple-900 mb-1">
                  Most Influential Causation Factor
                </div>
                <div className="text-sm text-purple-800">
                  <strong>{causationFactorAnalysis.sort((a, b) => b.current_avg_value - a.current_avg_value)[0].factor_name}</strong>
                  {' '}has the highest average value ({causationFactorAnalysis.sort((a, b) => b.current_avg_value - a.current_avg_value)[0].current_avg_value.toFixed(3)}).
                  Improving this factor by 10% would increase predictions by ${(causationFactorAnalysis.sort((a, b) => b.current_avg_value - a.current_avg_value)[0].impact_on_prediction / 1000).toFixed(1)}K on average.
                </div>
              </div>
            )}

            {/* Coefficient recommendation */}
            {coefficientImpactSummary.length === 0 && (
              <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="font-semibold text-gray-900 mb-1">
                  No Coefficient Changes
                </div>
                <div className="text-sm text-gray-700">
                  You're currently using default coefficients. Try adjusting C1 (severity influence) or C2 (impact influence) to see how it affects individual factors.
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
