import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ClaimData, WeightConfig } from '../../types/claims';
import { performSensitivityAnalysis } from '../../utils/recalibrationEngine';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';

interface SensitivityAnalysisChartProps {
  claims: ClaimData[];
  weights: WeightConfig[];
  baseWeights: Map<string, number>;
}

export default function SensitivityAnalysisChart({
  claims,
  weights,
  baseWeights,
}: SensitivityAnalysisChartProps) {
  const [selectedFactor, setSelectedFactor] = useState<string>(weights[0]?.factor_name || '');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const selectedWeight = useMemo(() => {
    return weights.find((w) => w.factor_name === selectedFactor);
  }, [weights, selectedFactor]);

  const sensitivityData = useMemo(() => {
    if (!selectedWeight || claims.length === 0) return [];

    // Generate test weights around the current value
    const currentWeight = baseWeights.get(selectedFactor) || selectedWeight.base_weight;
    const step = (selectedWeight.max_weight - selectedWeight.min_weight) / 20;
    const testWeights: number[] = [];

    for (let i = 0; i <= 20; i++) {
      const weight = selectedWeight.min_weight + step * i;
      testWeights.push(weight);
    }

    const results = performSensitivityAnalysis(claims, baseWeights, selectedFactor, testWeights);

    return results.map((r) => ({
      weight: r.weight,
      mape: r.mape,
      rmse: r.rmse / 1000, // Convert to thousands for readability
      isCurrent: Math.abs(r.weight - currentWeight) < 0.001,
      isRecommended: Math.abs(r.weight - selectedWeight.recommended_weight) < 0.001,
    }));
  }, [claims, selectedFactor, selectedWeight, baseWeights]);

  const filteredWeights = useMemo(() => {
    if (selectedCategory === 'all') return weights;
    return weights.filter((w) => w.category === selectedCategory);
  }, [weights, selectedCategory]);

  const categories = ['all', ...Array.from(new Set(weights.map((w) => w.category)))];

  // Find optimal weight (lowest MAPE)
  const optimalPoint = useMemo(() => {
    if (sensitivityData.length === 0) return null;
    return sensitivityData.reduce((min, curr) => (curr.mape < min.mape ? curr : min));
  }, [sensitivityData]);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Sensitivity Analysis Controls</CardTitle>
          <CardDescription>
            Analyze how changes to a single factor weight affect overall model performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Category Filter</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Factor to Analyze</Label>
              <Select value={selectedFactor} onValueChange={setSelectedFactor}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {filteredWeights.map((weight) => (
                    <SelectItem key={weight.factor_name} value={weight.factor_name}>
                      {weight.factor_name} ({weight.category})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {selectedWeight && (
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <p className="text-sm font-semibold mb-2">{selectedWeight.description}</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Min Weight:</span>
                  <div className="font-semibold">{selectedWeight.min_weight.toFixed(3)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Base Weight:</span>
                  <div className="font-semibold">{selectedWeight.base_weight.toFixed(3)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Recommended:</span>
                  <div className="font-semibold">{selectedWeight.recommended_weight.toFixed(3)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Max Weight:</span>
                  <div className="font-semibold">{selectedWeight.max_weight.toFixed(3)}</div>
                </div>
              </div>
            </div>
          )}

          {optimalPoint && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm font-semibold text-blue-900 mb-2">Optimal Weight Detected</p>
              <p className="text-sm text-blue-800">
                The optimal weight for {selectedFactor} appears to be{' '}
                <span className="font-bold">{optimalPoint.weight.toFixed(3)}</span> with a MAPE of{' '}
                <span className="font-bold">{optimalPoint.mape.toFixed(2)}%</span>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* MAPE Sensitivity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>MAPE Sensitivity Curve</CardTitle>
          <CardDescription>
            How prediction error (MAPE) changes with weight adjustments
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={sensitivityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="weight"
                label={{ value: 'Weight Value', position: 'insideBottom', offset: -5 }}
                domain={['dataMin', 'dataMax']}
              />
              <YAxis
                label={{ value: 'MAPE (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <p className="font-semibold">Weight: {data.weight.toFixed(3)}</p>
                        <p className="text-sm">MAPE: {data.mape.toFixed(2)}%</p>
                        {data.isCurrent && <p className="text-sm text-blue-600 font-semibold">Current Weight</p>}
                        {data.isRecommended && <p className="text-sm text-green-600 font-semibold">Recommended Weight</p>}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="mape"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.isCurrent) {
                    return <circle cx={cx} cy={cy} r={6} fill="#3b82f6" stroke="#fff" strokeWidth={2} />;
                  }
                  if (payload.isRecommended) {
                    return <circle cx={cx} cy={cy} r={6} fill="#10b981" stroke="#fff" strokeWidth={2} />;
                  }
                  return <circle cx={cx} cy={cy} r={3} fill="#3b82f6" />;
                }}
                name="MAPE"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* RMSE Sensitivity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>RMSE Sensitivity Curve</CardTitle>
          <CardDescription>
            How root mean square error changes with weight adjustments
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={sensitivityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="weight"
                label={{ value: 'Weight Value', position: 'insideBottom', offset: -5 }}
                domain={['dataMin', 'dataMax']}
              />
              <YAxis
                label={{ value: 'RMSE ($1000s)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <p className="font-semibold">Weight: {data.weight.toFixed(3)}</p>
                        <p className="text-sm">RMSE: ${data.rmse.toFixed(1)}k</p>
                        {data.isCurrent && <p className="text-sm text-blue-600 font-semibold">Current Weight</p>}
                        {data.isRecommended && <p className="text-sm text-green-600 font-semibold">Recommended Weight</p>}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="rmse"
                stroke="#ef4444"
                strokeWidth={2}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.isCurrent) {
                    return <circle cx={cx} cy={cy} r={6} fill="#ef4444" stroke="#fff" strokeWidth={2} />;
                  }
                  if (payload.isRecommended) {
                    return <circle cx={cx} cy={cy} r={6} fill="#10b981" stroke="#fff" strokeWidth={2} />;
                  }
                  return <circle cx={cx} cy={cy} r={3} fill="#ef4444" />;
                }}
                name="RMSE ($1000s)"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
