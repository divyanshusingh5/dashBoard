import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ReferenceLine, BarChart, Bar } from 'recharts';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { ClaimData } from '../../types/claims';
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import FactorWeightComparison from './FactorWeightComparison';

interface SingleInjuryRecalibrationProps {
  claims: ClaimData[];
}

// Default coefficients for the equation: y = e^(C0 + C1*S + C2*I + C3*S*I + C4*I^2 + C5*I^3 + C6*S^2)
const DEFAULT_COEFFICIENTS = {
  C0: 10.5,    // Base constant
  C1: 0.15,    // Severity coefficient
  C2: 0.25,    // Impact coefficient
  C3: 0.05,    // Severity * Impact interaction
  C4: -0.1,    // Impact^2 (quadratic)
  C5: 0.02,    // Impact^3 (cubic)
  C6: -0.01,   // Severity^2 (quadratic)
};

export default function SingleInjuryRecalibration({ claims }: SingleInjuryRecalibrationProps) {
  const [coefficients, setCoefficients] = useState(DEFAULT_COEFFICIENTS);
  const [useRecentOnly, setUseRecentOnly] = useState<boolean>(true);

  // Filter for single injury claims only
  const singleInjuryClaims = useMemo(() => {
    let filtered = claims.filter(claim => {
      // Single injury: INJURY_COUNT === 1 or only one injury type
      return claim.INJURY_COUNT === 1 || claim.Injury_Count === 'Single';
    });

    // Filter by date if requested
    if (useRecentOnly) {
      filtered = filtered.filter(claim => {
        const claimYear = new Date(claim.claim_date).getFullYear();
        return claimYear >= 2024;
      });
    }

    return filtered;
  }, [claims, useRecentOnly]);

  // Calculate severity sum for a claim
  const calculateSeveritySum = (claim: ClaimData): number => {
    let sum = 0;

    // Add numeric severity score if available
    if (claim.SEVERITY_SCORE) {
      sum += parseFloat(String(claim.SEVERITY_SCORE));
    }

    // Add severity factors (normalized to 0-1)
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
        if (!isNaN(numValue)) {
          sum += numValue;
        }
      }
    });

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
        if (!isNaN(numValue)) {
          sum += numValue;
        }
      }
    });

    return sum;
  };

  // Get impact score (1-4)
  const getImpactScore = (claim: ClaimData): number => {
    // IMPACT field in data (1, 2, 3, or 4)
    if (claim.IMPACT) {
      const impact = typeof claim.IMPACT === 'number' ? claim.IMPACT : parseInt(String(claim.IMPACT));
      return Math.min(4, Math.max(1, impact)); // Clamp to 1-4
    }
    return 2; // Default medium impact
  };

  // Calculate prediction using the equation: y = e^(C0 + C1*S + C2*I + C3*S*I + C4*I^2 + C5*I^3 + C6*S^2)
  const calculatePrediction = (
    claim: ClaimData,
    coefs: typeof DEFAULT_COEFFICIENTS
  ): number => {
    const S = calculateSeveritySum(claim);
    const I = getImpactScore(claim);
    const ratingWeight = claim.RATINGWEIGHT || 0;
    const causationSum = calculateCausationSum(claim);

    // Core equation
    const exponent =
      coefs.C0 +
      coefs.C1 * S +
      coefs.C2 * I +
      coefs.C3 * S * I +
      coefs.C4 * Math.pow(I, 2) +
      coefs.C5 * Math.pow(I, 3) +
      coefs.C6 * Math.pow(S, 2);

    const basePrediction = Math.exp(exponent);

    // Apply multipliers
    const adjustedPrediction = basePrediction * (1 + ratingWeight) * (1 + causationSum * 0.1);

    return adjustedPrediction;
  };

  // Recalibration analysis
  const recalibrationAnalysis = useMemo(() => {
    if (singleInjuryClaims.length === 0) {
      return null;
    }

    const results = singleInjuryClaims.map(claim => {
      const baselinePrediction = calculatePrediction(claim, DEFAULT_COEFFICIENTS);
      const testPrediction = calculatePrediction(claim, coefficients);
      const actual = claim.DOLLARAMOUNTHIGH;

      const baselineError = Math.abs(baselinePrediction - actual);
      const testError = Math.abs(testPrediction - actual);

      const baselineErrorPct = (baselineError / actual) * 100;
      const testErrorPct = (testError / actual) * 100;

      const improvement = baselineErrorPct - testErrorPct;

      return {
        claim_id: claim.claim_id,
        severity_sum: calculateSeveritySum(claim),
        impact_score: getImpactScore(claim),
        causation_sum: calculateCausationSum(claim),
        rating_weight: claim.RATINGWEIGHT || 0,
        actual,
        baseline_prediction: baselinePrediction,
        test_prediction: testPrediction,
        baseline_error: baselineError,
        test_error: testError,
        baseline_error_pct: baselineErrorPct,
        test_error_pct: testErrorPct,
        improvement_pct: improvement,
      };
    });

    // Calculate aggregate metrics
    const avgBaselineError = results.reduce((sum, r) => sum + r.baseline_error, 0) / results.length;
    const avgTestError = results.reduce((sum, r) => sum + r.test_error, 0) / results.length;
    const avgBaselineErrorPct = results.reduce((sum, r) => sum + r.baseline_error_pct, 0) / results.length;
    const avgTestErrorPct = results.reduce((sum, r) => sum + r.test_error_pct, 0) / results.length;
    const avgImprovement = results.reduce((sum, r) => sum + r.improvement_pct, 0) / results.length;

    const improved = results.filter(r => r.improvement_pct > 1).length;
    const degraded = results.filter(r => r.improvement_pct < -1).length;

    const rmseBaseline = Math.sqrt(
      results.reduce((sum, r) => sum + Math.pow(r.baseline_error, 2), 0) / results.length
    );
    const rmseTest = Math.sqrt(
      results.reduce((sum, r) => sum + Math.pow(r.test_error, 2), 0) / results.length
    );

    // R-squared calculation
    const actualMean = results.reduce((sum, r) => sum + r.actual, 0) / results.length;
    const ssTot = results.reduce((sum, r) => sum + Math.pow(r.actual - actualMean, 2), 0);
    const ssResBaseline = results.reduce((sum, r) => sum + Math.pow(r.actual - r.baseline_prediction, 2), 0);
    const ssResTest = results.reduce((sum, r) => sum + Math.pow(r.actual - r.test_prediction, 2), 0);

    const r2Baseline = 1 - (ssResBaseline / ssTot);
    const r2Test = 1 - (ssResTest / ssTot);

    return {
      results,
      metrics: {
        claims_analyzed: results.length,
        avg_baseline_error: avgBaselineError,
        avg_test_error: avgTestError,
        avg_baseline_error_pct: avgBaselineErrorPct,
        avg_test_error_pct: avgTestErrorPct,
        avg_improvement_pct: avgImprovement,
        rmse_baseline: rmseBaseline,
        rmse_test: rmseTest,
        rmse_improvement_pct: ((rmseBaseline - rmseTest) / rmseBaseline) * 100,
        r2_baseline: r2Baseline,
        r2_test: r2Test,
        improved_count: improved,
        degraded_count: degraded,
      }
    };
  }, [singleInjuryClaims, coefficients]);

  // Scatter plot data: Actual vs Predicted
  const scatterData = useMemo(() => {
    if (!recalibrationAnalysis) return [];

    return recalibrationAnalysis.results.map(r => ({
      actual: r.actual,
      baseline: r.baseline_prediction,
      test: r.test_prediction,
      claim_id: r.claim_id,
    }));
  }, [recalibrationAnalysis]);

  // Error distribution data
  const errorDistribution = useMemo(() => {
    if (!recalibrationAnalysis) return [];

    const bins = [
      { range: '0-10%', min: 0, max: 10, baseline: 0, test: 0 },
      { range: '10-20%', min: 10, max: 20, baseline: 0, test: 0 },
      { range: '20-30%', min: 20, max: 30, baseline: 0, test: 0 },
      { range: '30-40%', min: 30, max: 40, baseline: 0, test: 0 },
      { range: '40-50%', min: 40, max: 50, baseline: 0, test: 0 },
      { range: '>50%', min: 50, max: Infinity, baseline: 0, test: 0 },
    ];

    recalibrationAnalysis.results.forEach(r => {
      bins.forEach(bin => {
        if (r.baseline_error_pct >= bin.min && r.baseline_error_pct < bin.max) {
          bin.baseline++;
        }
        if (r.test_error_pct >= bin.min && r.test_error_pct < bin.max) {
          bin.test++;
        }
      });
    });

    return bins;
  }, [recalibrationAnalysis]);

  const handleCoefficientChange = (key: keyof typeof DEFAULT_COEFFICIENTS, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      setCoefficients(prev => ({ ...prev, [key]: numValue }));
    }
  };

  const handleReset = () => {
    setCoefficients(DEFAULT_COEFFICIENTS);
  };

  const metrics = recalibrationAnalysis?.metrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle>Single Injury Recalibration</CardTitle>
          <CardDescription>
            Equation: y = e^(C0 + C1·S + C2·I + C3·S·I + C4·I² + C5·I³ + C6·S²) × (1 + RatingWeight) × (1 + 0.1·CausationSum)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Data Filter */}
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <Button
                variant={useRecentOnly ? 'default' : 'outline'}
                onClick={() => setUseRecentOnly(true)}
              >
                Recent (2024-2025)
              </Button>
              <Button
                variant={!useRecentOnly ? 'default' : 'outline'}
                onClick={() => setUseRecentOnly(false)}
              >
                All Data
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-lg px-4 py-2">
                {singleInjuryClaims.length} Single Injury Claims
              </Badge>
              <Button variant="outline" size="sm" onClick={handleReset}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset Coefficients
              </Button>
            </div>
          </div>

          {/* Coefficient Inputs */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-4">Adjust Coefficients</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(coefficients).map(([key, value]) => (
                <div key={key} className="space-y-1">
                  <Label htmlFor={key} className="text-sm font-medium">
                    {key}
                  </Label>
                  <Input
                    id={key}
                    type="number"
                    step="0.001"
                    value={value}
                    onChange={(e) => handleCoefficientChange(key as keyof typeof DEFAULT_COEFFICIENTS, e.target.value)}
                    className="font-mono"
                  />
                  <p className="text-xs text-muted-foreground">
                    Default: {DEFAULT_COEFFICIENTS[key as keyof typeof DEFAULT_COEFFICIENTS]}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Equation Breakdown */}
          <div className="bg-gray-50 border rounded-lg p-4">
            <h4 className="font-semibold mb-2">Variable Definitions:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              <div><strong>S</strong> = Sum of severity scores (severity_* factors)</div>
              <div><strong>I</strong> = Impact score (1-4 from IMPACT field)</div>
              <div><strong>RatingWeight</strong> = Venue rating weight (RATINGWEIGHT)</div>
              <div><strong>CausationSum</strong> = Sum of causation factors (causation_*)</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Error Change</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.avg_improvement_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {metrics.avg_improvement_pct > 0 ? '+' : ''}{metrics.avg_improvement_pct.toFixed(2)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {metrics.avg_baseline_error_pct.toFixed(1)}% → {metrics.avg_test_error_pct.toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">RMSE Impact</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.rmse_improvement_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {metrics.rmse_improvement_pct > 0 ? '+' : ''}{metrics.rmse_improvement_pct.toFixed(2)}%
              </div>
              <p className="text-xs text-muted-foreground">
                ${(metrics.rmse_baseline / 1000).toFixed(1)}K → ${(metrics.rmse_test / 1000).toFixed(1)}K
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">R² Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.r2_test > metrics.r2_baseline ? 'text-green-600' : 'text-red-600'}`}>
                {metrics.r2_test.toFixed(3)}
              </div>
              <p className="text-xs text-muted-foreground">
                Was: {metrics.r2_baseline.toFixed(3)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Improved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {metrics.improved_count}
              </div>
              <p className="text-xs text-muted-foreground">
                {((metrics.improved_count / metrics.claims_analyzed) * 100).toFixed(1)}% of claims
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Degraded</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {metrics.degraded_count}
              </div>
              <p className="text-xs text-muted-foreground">
                {((metrics.degraded_count / metrics.claims_analyzed) * 100).toFixed(1)}% of claims
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analysis Tabs */}
      {recalibrationAnalysis && (
        <Tabs defaultValue="charts" className="space-y-4">
          <TabsList>
            <TabsTrigger value="charts">Performance Charts</TabsTrigger>
            <TabsTrigger value="factors">Factor Analysis</TabsTrigger>
          </TabsList>

          {/* Charts Tab */}
          <TabsContent value="charts" className="space-y-6">
            {/* Charts content */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Actual vs Predicted Scatter */}
              <Card>
                <CardHeader>
                  <CardTitle>Actual vs Predicted Values</CardTitle>
                  <CardDescription>
                    Perfect predictions fall on the diagonal line
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        type="number"
                        dataKey="actual"
                        name="Actual"
                        label={{ value: 'Actual DOLLARAMOUNTHIGH', position: 'insideBottom', offset: -5 }}
                        tickFormatter={(val) => `$${(val / 1000).toFixed(0)}K`}
                      />
                      <YAxis
                        type="number"
                        dataKey="test"
                        name="Predicted"
                        label={{ value: 'Predicted Value', angle: -90, position: 'insideLeft' }}
                        tickFormatter={(val) => `$${(val / 1000).toFixed(0)}K`}
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload[0]) {
                            const data = payload[0].payload;
                            return (
                              <div className="bg-white p-3 border rounded shadow-lg">
                                <p className="font-semibold">{data.claim_id}</p>
                                <p className="text-sm">Actual: ${(data.actual / 1000).toFixed(1)}K</p>
                                <p className="text-sm text-green-600">Test: ${(data.test / 1000).toFixed(1)}K</p>
                                <p className="text-sm text-gray-500">Baseline: ${(data.baseline / 1000).toFixed(1)}K</p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <ReferenceLine
                        stroke="#666"
                        strokeDasharray="3 3"
                        segment={[
                          { x: 0, y: 0 },
                          { x: 200000, y: 200000 }
                        ]}
                      />
                      <Scatter
                        name="Test Predictions"
                        data={scatterData}
                        fill="#10b981"
                        fillOpacity={0.6}
                      />
                      <Scatter
                        name="Baseline Predictions"
                        data={scatterData.map(d => ({ ...d, test: d.baseline }))}
                        fill="#ef4444"
                        fillOpacity={0.3}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Error Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Error Distribution</CardTitle>
                  <CardDescription>
                    Count of claims by error percentage range
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={errorDistribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="range" />
                      <YAxis label={{ value: 'Number of Claims', angle: -90, position: 'insideLeft' }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="baseline" name="Baseline" fill="#ef4444" />
                      <Bar dataKey="test" name="Test" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Top Improved/Degraded Claims */}
            <Card>
              <CardHeader>
                <CardTitle>Claim-Level Impact Details</CardTitle>
                <CardDescription>
                  Top 10 most improved and most degraded claims
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Most Improved */}
                  <div>
                    <h4 className="font-semibold text-green-600 mb-3">Most Improved Claims</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2">Claim ID</th>
                            <th className="text-right p-2">S</th>
                            <th className="text-right p-2">I</th>
                            <th className="text-right p-2">Actual</th>
                            <th className="text-right p-2">Improve</th>
                          </tr>
                        </thead>
                        <tbody>
                          {recalibrationAnalysis.results
                            .sort((a, b) => b.improvement_pct - a.improvement_pct)
                            .slice(0, 10)
                            .map((result) => (
                              <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                                <td className="p-2 font-medium">{result.claim_id}</td>
                                <td className="p-2 text-right">{result.severity_sum.toFixed(1)}</td>
                                <td className="p-2 text-right">{result.impact_score}</td>
                                <td className="p-2 text-right">${(result.actual / 1000).toFixed(1)}K</td>
                                <td className="p-2 text-right text-green-600 font-semibold">
                                  +{result.improvement_pct.toFixed(2)}%
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Most Degraded */}
                  <div>
                    <h4 className="font-semibold text-red-600 mb-3">Most Degraded Claims</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2">Claim ID</th>
                            <th className="text-right p-2">S</th>
                            <th className="text-right p-2">I</th>
                            <th className="text-right p-2">Actual</th>
                            <th className="text-right p-2">Change</th>
                          </tr>
                        </thead>
                        <tbody>
                          {recalibrationAnalysis.results
                            .sort((a, b) => a.improvement_pct - b.improvement_pct)
                            .slice(0, 10)
                            .map((result) => (
                              <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                                <td className="p-2 font-medium">{result.claim_id}</td>
                                <td className="p-2 text-right">{result.severity_sum.toFixed(1)}</td>
                                <td className="p-2 text-right">{result.impact_score}</td>
                                <td className="p-2 text-right">${(result.actual / 1000).toFixed(1)}K</td>
                                <td className="p-2 text-right text-red-600 font-semibold">
                                  {result.improvement_pct.toFixed(2)}%
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Factor Analysis Tab */}
          <TabsContent value="factors" className="space-y-6">
            <FactorWeightComparison
              claims={singleInjuryClaims}
              coefficients={coefficients}
              defaultCoefficients={DEFAULT_COEFFICIENTS}
            />
          </TabsContent>
        </Tabs>
      )}

      {/* Remove duplicate charts section */}
      {false && recalibrationAnalysis && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Actual vs Predicted Scatter */}
          <Card>
            <CardHeader>
              <CardTitle>Actual vs Predicted Values</CardTitle>
              <CardDescription>
                Perfect predictions fall on the diagonal line
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="actual"
                    name="Actual"
                    label={{ value: 'Actual DOLLARAMOUNTHIGH', position: 'insideBottom', offset: -5 }}
                    tickFormatter={(val) => `$${(val / 1000).toFixed(0)}K`}
                  />
                  <YAxis
                    type="number"
                    dataKey="test"
                    name="Predicted"
                    label={{ value: 'Predicted Value', angle: -90, position: 'insideLeft' }}
                    tickFormatter={(val) => `$${(val / 1000).toFixed(0)}K`}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload[0]) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 border rounded shadow-lg">
                            <p className="font-semibold">{data.claim_id}</p>
                            <p className="text-sm">Actual: ${(data.actual / 1000).toFixed(1)}K</p>
                            <p className="text-sm text-green-600">Test: ${(data.test / 1000).toFixed(1)}K</p>
                            <p className="text-sm text-gray-500">Baseline: ${(data.baseline / 1000).toFixed(1)}K</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <ReferenceLine
                    stroke="#666"
                    strokeDasharray="3 3"
                    segment={[
                      { x: 0, y: 0 },
                      { x: 200000, y: 200000 }
                    ]}
                  />
                  <Scatter
                    name="Test Predictions"
                    data={scatterData}
                    fill="#10b981"
                    fillOpacity={0.6}
                  />
                  <Scatter
                    name="Baseline Predictions"
                    data={scatterData.map(d => ({ ...d, test: d.baseline }))}
                    fill="#ef4444"
                    fillOpacity={0.3}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Error Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Error Distribution</CardTitle>
              <CardDescription>
                Count of claims by error percentage range
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={errorDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis label={{ value: 'Number of Claims', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="baseline" name="Baseline" fill="#ef4444" />
                  <Bar dataKey="test" name="Test" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Top Improved/Degraded Claims */}
      {recalibrationAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle>Claim-Level Impact Details</CardTitle>
            <CardDescription>
              Top 10 most improved and most degraded claims
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Most Improved */}
              <div>
                <h4 className="font-semibold text-green-600 mb-3">Most Improved Claims</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Claim ID</th>
                        <th className="text-right p-2">S</th>
                        <th className="text-right p-2">I</th>
                        <th className="text-right p-2">Actual</th>
                        <th className="text-right p-2">Improve</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recalibrationAnalysis.results
                        .sort((a, b) => b.improvement_pct - a.improvement_pct)
                        .slice(0, 10)
                        .map((result) => (
                          <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                            <td className="p-2 font-medium">{result.claim_id}</td>
                            <td className="p-2 text-right">{result.severity_sum.toFixed(1)}</td>
                            <td className="p-2 text-right">{result.impact_score}</td>
                            <td className="p-2 text-right">${(result.actual / 1000).toFixed(1)}K</td>
                            <td className="p-2 text-right text-green-600 font-semibold">
                              +{result.improvement_pct.toFixed(2)}%
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Most Degraded */}
              <div>
                <h4 className="font-semibold text-red-600 mb-3">Most Degraded Claims</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Claim ID</th>
                        <th className="text-right p-2">S</th>
                        <th className="text-right p-2">I</th>
                        <th className="text-right p-2">Actual</th>
                        <th className="text-right p-2">Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recalibrationAnalysis.results
                        .sort((a, b) => a.improvement_pct - b.improvement_pct)
                        .slice(0, 10)
                        .map((result) => (
                          <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                            <td className="p-2 font-medium">{result.claim_id}</td>
                            <td className="p-2 text-right">{result.severity_sum.toFixed(1)}</td>
                            <td className="p-2 text-right">{result.impact_score}</td>
                            <td className="p-2 text-right">${(result.actual / 1000).toFixed(1)}K</td>
                            <td className="p-2 text-right text-red-600 font-semibold">
                              {result.improvement_pct.toFixed(2)}%
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Data Message */}
      {singleInjuryClaims.length === 0 && (
        <Card className="bg-gray-50">
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              <p className="text-lg font-medium mb-2">No Single Injury Claims Found</p>
              <p className="text-sm">
                Try selecting "All Data" or check if your claims have INJURY_COUNT === 1
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
