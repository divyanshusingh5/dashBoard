import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ReferenceLine } from 'recharts';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Slider } from '../ui/slider';
import { ClaimData, WeightConfig } from '../../types/claims';
import { calculateWeightedScore, categoricalToNumeric, WEIGHT_FACTORS } from '../../utils/recalibrationEngine';

interface FactorWeightImpactAnalyzerProps {
  claims: ClaimData[];
  weights: WeightConfig[];
}

export default function FactorWeightImpactAnalyzer({
  claims,
  weights,
}: FactorWeightImpactAnalyzerProps) {
  const [selectedFactor, setSelectedFactor] = useState<string>('');
  const [testWeightValue, setTestWeightValue] = useState<number>(0.1);
  const [useRecentOnly, setUseRecentOnly] = useState<boolean>(true);

  // Filter for recent claims (2024-2025)
  const filteredClaims = useMemo(() => {
    if (!useRecentOnly) return claims;

    return claims.filter(claim => {
      const claimYear = new Date(claim.claim_date).getFullYear();
      return claimYear >= 2024;
    });
  }, [claims, useRecentOnly]);

  // Get weight config for selected factor
  const selectedWeightConfig = useMemo(() => {
    return weights.find(w => w.factor_name === selectedFactor);
  }, [weights, selectedFactor]);

  // Calculate impact when changing just the selected factor weight
  const impactAnalysis = useMemo(() => {
    if (!selectedFactor || !selectedWeightConfig || filteredClaims.length === 0) {
      return null;
    }

    // Create baseline weight map (all at base_weight)
    const baselineWeights = new Map<string, number>();
    weights.forEach(w => baselineWeights.set(w.factor_name, w.base_weight));

    // Create test weight map (only selected factor changed)
    const testWeights = new Map(baselineWeights);
    testWeights.set(selectedFactor, testWeightValue);

    // Calculate predictions for each claim
    const results = filteredClaims.map(claim => {
      const baselineScore = calculateWeightedScore(claim, baselineWeights);
      const testScore = calculateWeightedScore(claim, testWeights);

      // Apply score differential to prediction
      const baselinePrediction = claim.predicted_pain_suffering * (1 + baselineScore);
      const testPrediction = claim.predicted_pain_suffering * (1 + testScore);

      const actualValue = claim.DOLLARAMOUNTHIGH;

      // Calculate errors
      const baselineError = Math.abs(baselinePrediction - actualValue);
      const testError = Math.abs(testPrediction - actualValue);

      const baselineErrorPct = (baselineError / actualValue) * 100;
      const testErrorPct = (testError / actualValue) * 100;

      const improvement = baselineErrorPct - testErrorPct;

      // Get factor value for this claim
      const factorValue = categoricalToNumeric(claim[selectedFactor as keyof ClaimData]);

      return {
        claim_id: claim.claim_id,
        actual: actualValue,
        baseline_prediction: baselinePrediction,
        test_prediction: testPrediction,
        baseline_error: baselineError,
        test_error: testError,
        baseline_error_pct: baselineErrorPct,
        test_error_pct: testErrorPct,
        improvement_pct: improvement,
        factor_value: factorValue,
        claim_date: claim.claim_date,
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
    const unchanged = results.filter(r => Math.abs(r.improvement_pct) <= 1).length;

    // Calculate RMSE
    const rmseBaseline = Math.sqrt(
      results.reduce((sum, r) => sum + Math.pow(r.baseline_error, 2), 0) / results.length
    );
    const rmseTest = Math.sqrt(
      results.reduce((sum, r) => sum + Math.pow(r.test_error, 2), 0) / results.length
    );

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
        improved_count: improved,
        degraded_count: degraded,
        unchanged_count: unchanged,
      }
    };
  }, [selectedFactor, selectedWeightConfig, testWeightValue, filteredClaims, weights]);

  // Chart data: Weight value vs Average Error
  const sensitivityChartData = useMemo(() => {
    if (!selectedFactor || !selectedWeightConfig || filteredClaims.length === 0) {
      return [];
    }

    const baselineWeights = new Map<string, number>();
    weights.forEach(w => baselineWeights.set(w.factor_name, w.base_weight));

    // Test multiple weight values from min to max
    const steps = 20;
    const minWeight = selectedWeightConfig.min_weight;
    const maxWeight = selectedWeightConfig.max_weight;
    const stepSize = (maxWeight - minWeight) / steps;

    const data = [];
    for (let i = 0; i <= steps; i++) {
      const weight = minWeight + (i * stepSize);
      const testWeights = new Map(baselineWeights);
      testWeights.set(selectedFactor, weight);

      let totalError = 0;
      let totalErrorPct = 0;

      filteredClaims.forEach(claim => {
        const score = calculateWeightedScore(claim, testWeights);
        const prediction = claim.predicted_pain_suffering * (1 + score);
        const actual = claim.DOLLARAMOUNTHIGH;
        const error = Math.abs(prediction - actual);
        const errorPct = (error / actual) * 100;

        totalError += error;
        totalErrorPct += errorPct;
      });

      const avgError = totalError / filteredClaims.length;
      const avgErrorPct = totalErrorPct / filteredClaims.length;

      data.push({
        weight: weight,
        avg_error: avgError,
        avg_error_pct: avgErrorPct,
        is_base: Math.abs(weight - selectedWeightConfig.base_weight) < 0.001,
        is_current: Math.abs(weight - testWeightValue) < 0.001,
      });
    }

    return data;
  }, [selectedFactor, selectedWeightConfig, filteredClaims, weights, testWeightValue]);

  // Scatter plot: Factor Value vs Impact
  const scatterData = useMemo(() => {
    if (!impactAnalysis) return [];

    return impactAnalysis.results.map(r => ({
      factor_value: r.factor_value,
      improvement_pct: r.improvement_pct,
      actual: r.actual,
      claim_id: r.claim_id,
    }));
  }, [impactAnalysis]);

  // Group claims by category
  const categorizedWeights = useMemo(() => {
    const grouped = new Map<string, WeightConfig[]>();
    weights.forEach(w => {
      const category = w.category;
      if (!grouped.has(category)) {
        grouped.set(category, []);
      }
      grouped.get(category)!.push(w);
    });
    return grouped;
  }, [weights]);

  const handleFactorChange = (factorName: string) => {
    setSelectedFactor(factorName);
    const config = weights.find(w => w.factor_name === factorName);
    if (config) {
      setTestWeightValue(config.base_weight);
    }
  };

  const metrics = impactAnalysis?.metrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle>Individual Factor Weight Impact Analysis</CardTitle>
          <CardDescription>
            Analyze how changing a single factor weight impacts DOLLARAMOUNTHIGH predictions while keeping all other weights constant
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Factor Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Select Factor to Analyze</label>
              <Select value={selectedFactor} onValueChange={handleFactorChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a factor..." />
                </SelectTrigger>
                <SelectContent className="max-h-96">
                  {Array.from(categorizedWeights.entries()).map(([category, factors]) => (
                    <div key={category}>
                      <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                        {category}
                      </div>
                      {factors.map(factor => (
                        <SelectItem key={factor.factor_name} value={factor.factor_name}>
                          {factor.factor_name}
                        </SelectItem>
                      ))}
                    </div>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Weight Value Slider */}
            {selectedWeightConfig && (
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Test Weight Value: {testWeightValue.toFixed(3)}
                </label>
                <Slider
                  value={[testWeightValue]}
                  onValueChange={(values) => setTestWeightValue(values[0])}
                  min={selectedWeightConfig.min_weight}
                  max={selectedWeightConfig.max_weight}
                  step={0.001}
                  className="mt-2"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Min: {selectedWeightConfig.min_weight}</span>
                  <span>Base: {selectedWeightConfig.base_weight.toFixed(3)}</span>
                  <span>Max: {selectedWeightConfig.max_weight}</span>
                </div>
              </div>
            )}

            {/* Data Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Data Range</label>
              <div className="flex gap-2">
                <Button
                  variant={useRecentOnly ? 'default' : 'outline'}
                  onClick={() => setUseRecentOnly(true)}
                  className="flex-1"
                >
                  Recent (2024-2025)
                </Button>
                <Button
                  variant={!useRecentOnly ? 'default' : 'outline'}
                  onClick={() => setUseRecentOnly(false)}
                  className="flex-1"
                >
                  All Data
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                {filteredClaims.length} claims analyzed
              </p>
            </div>
          </div>

          {/* Selected Factor Info */}
          {selectedWeightConfig && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-blue-900">
                    {selectedWeightConfig.factor_name}
                  </h4>
                  <p className="text-sm text-blue-700 mt-1">
                    {selectedWeightConfig.description}
                  </p>
                  <div className="flex gap-2 mt-2">
                    <Badge variant="outline">{selectedWeightConfig.category}</Badge>
                    <Badge variant="secondary">
                      Base: {selectedWeightConfig.base_weight.toFixed(3)}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
              <CardTitle className="text-sm font-medium">Improved Claims</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {metrics.improved_count}
              </div>
              <p className="text-xs text-muted-foreground">
                {((metrics.improved_count / metrics.claims_analyzed) * 100).toFixed(1)}% of {metrics.claims_analyzed}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Degraded Claims</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {metrics.degraded_count}
              </div>
              <p className="text-xs text-muted-foreground">
                {((metrics.degraded_count / metrics.claims_analyzed) * 100).toFixed(1)}% of {metrics.claims_analyzed}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts */}
      {selectedFactor && impactAnalysis && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sensitivity Curve */}
          <Card>
            <CardHeader>
              <CardTitle>Weight Sensitivity Curve</CardTitle>
              <CardDescription>
                How average prediction error changes as weight varies from min to max
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={sensitivityChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="weight"
                    label={{ value: 'Weight Value', position: 'insideBottom', offset: -5 }}
                    tickFormatter={(val) => val.toFixed(3)}
                  />
                  <YAxis
                    label={{ value: 'Avg Error %', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload[0]) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 border rounded shadow-lg">
                            <p className="font-semibold">Weight: {data.weight.toFixed(3)}</p>
                            <p className="text-sm">Avg Error: {data.avg_error_pct.toFixed(2)}%</p>
                            <p className="text-sm text-muted-foreground">
                              ${(data.avg_error / 1000).toFixed(1)}K
                            </p>
                            {data.is_base && (
                              <p className="text-xs text-blue-600 font-semibold mt-1">BASE VALUE</p>
                            )}
                            {data.is_current && (
                              <p className="text-xs text-green-600 font-semibold mt-1">CURRENT TEST</p>
                            )}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="avg_error_pct"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={(props) => {
                      const { cx, cy, payload } = props;
                      if (payload.is_base) {
                        return <circle cx={cx} cy={cy} r={6} fill="#ef4444" stroke="#fff" strokeWidth={2} />;
                      }
                      if (payload.is_current) {
                        return <circle cx={cx} cy={cy} r={6} fill="#10b981" stroke="#fff" strokeWidth={2} />;
                      }
                      return <circle cx={cx} cy={cy} r={3} fill="#3b82f6" />;
                    }}
                  />
                  {selectedWeightConfig && (
                    <>
                      <ReferenceLine
                        x={selectedWeightConfig.base_weight}
                        stroke="#ef4444"
                        strokeDasharray="3 3"
                        label={{ value: 'Base', position: 'top', fill: '#ef4444' }}
                      />
                      <ReferenceLine
                        x={testWeightValue}
                        stroke="#10b981"
                        strokeDasharray="3 3"
                        label={{ value: 'Test', position: 'top', fill: '#10b981' }}
                      />
                    </>
                  )}
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 flex gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <span>Base Weight</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span>Test Weight</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Factor Value vs Improvement Scatter */}
          <Card>
            <CardHeader>
              <CardTitle>Factor Value vs Impact</CardTitle>
              <CardDescription>
                How improvement varies with the factor's value in each claim
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="factor_value"
                    name="Factor Value"
                    label={{ value: 'Factor Value (normalized)', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="improvement_pct"
                    name="Improvement %"
                    label={{ value: 'Improvement %', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload[0]) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 border rounded shadow-lg">
                            <p className="font-semibold">{data.claim_id}</p>
                            <p className="text-sm">Factor Value: {data.factor_value.toFixed(3)}</p>
                            <p className="text-sm">Improvement: {data.improvement_pct.toFixed(2)}%</p>
                            <p className="text-sm text-muted-foreground">
                              Actual: ${(data.actual / 1000).toFixed(1)}K
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                  <Scatter
                    name="Claims"
                    data={scatterData}
                    fill="#3b82f6"
                    fillOpacity={0.6}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Top Improved/Degraded Claims Table */}
      {impactAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle>Claim-Level Impact Details</CardTitle>
            <CardDescription>
              Top 10 most improved and most degraded claims from weight change
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
                        <th className="text-right p-2">Actual</th>
                        <th className="text-right p-2">Improvement</th>
                      </tr>
                    </thead>
                    <tbody>
                      {impactAnalysis.results
                        .sort((a, b) => b.improvement_pct - a.improvement_pct)
                        .slice(0, 10)
                        .map((result) => (
                          <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                            <td className="p-2 font-medium">{result.claim_id}</td>
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
                        <th className="text-right p-2">Actual</th>
                        <th className="text-right p-2">Degradation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {impactAnalysis.results
                        .sort((a, b) => a.improvement_pct - b.improvement_pct)
                        .slice(0, 10)
                        .map((result) => (
                          <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                            <td className="p-2 font-medium">{result.claim_id}</td>
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

      {/* Instructions */}
      {!selectedFactor && (
        <Card className="bg-gray-50">
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              <p className="text-lg font-medium mb-2">Get Started</p>
              <p className="text-sm">
                Select a factor above to analyze how changing its weight impacts DOLLARAMOUNTHIGH predictions.
                All other factor weights remain constant during analysis.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
