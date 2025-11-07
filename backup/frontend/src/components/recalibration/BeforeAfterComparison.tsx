import React, { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { RecalibrationResult, RecalibrationMetrics } from '../../types/claims';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { Badge } from '../ui/badge';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface BeforeAfterComparisonProps {
  results: RecalibrationResult[];
  metrics: RecalibrationMetrics;
}

export default function BeforeAfterComparison({
  results,
  metrics,
}: BeforeAfterComparisonProps) {
  const [showTopN, setShowTopN] = useState(20);

  // Scatter plot data
  const scatterData = useMemo(() => {
    return results.map((r) => ({
      claim_id: r.claim_id,
      actual: r.actual_value,
      original: r.original_prediction,
      recalibrated: r.recalibrated_prediction,
      improvement: r.improvement_pct,
    }));
  }, [results]);

  // Top improved claims
  const topImproved = useMemo(() => {
    return [...results]
      .sort((a, b) => b.improvement_pct - a.improvement_pct)
      .slice(0, showTopN);
  }, [results, showTopN]);

  // Variance distribution
  const varianceDistribution = useMemo(() => {
    const buckets = [
      { range: '0-5%', min: 0, max: 5, before: 0, after: 0 },
      { range: '5-10%', min: 5, max: 10, before: 0, after: 0 },
      { range: '10-15%', min: 10, max: 15, before: 0, after: 0 },
      { range: '15-20%', min: 15, max: 20, before: 0, after: 0 },
      { range: '20-30%', min: 20, max: 30, before: 0, after: 0 },
      { range: '30%+', min: 30, max: Infinity, before: 0, after: 0 },
    ];

    results.forEach((r) => {
      for (const bucket of buckets) {
        if (r.original_variance_pct >= bucket.min && r.original_variance_pct < bucket.max) {
          bucket.before++;
        }
        if (r.recalibrated_variance_pct >= bucket.min && r.recalibrated_variance_pct < bucket.max) {
          bucket.after++;
        }
      }
    });

    return buckets;
  }, [results]);

  return (
    <div className="space-y-6">
      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">MAPE Improvement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{metrics.mape_before.toFixed(2)}%</span>
              <span className="text-muted-foreground">→</span>
              <span className="text-2xl font-bold text-green-600">{metrics.mape_after.toFixed(2)}%</span>
            </div>
            <div className="flex items-center mt-2">
              {metrics.mape_after < metrics.mape_before ? (
                <>
                  <TrendingDown className="h-4 w-4 text-green-600 mr-1" />
                  <span className="text-sm text-green-600">
                    {((metrics.mape_before - metrics.mape_after) / metrics.mape_before * 100).toFixed(1)}% improvement
                  </span>
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4 text-red-600 mr-1" />
                  <span className="text-sm text-red-600">
                    {((metrics.mape_after - metrics.mape_before) / metrics.mape_before * 100).toFixed(1)}% degradation
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">RMSE Improvement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">${(metrics.rmse_before / 1000).toFixed(1)}k</span>
              <span className="text-muted-foreground">→</span>
              <span className="text-2xl font-bold text-green-600">${(metrics.rmse_after / 1000).toFixed(1)}k</span>
            </div>
            <div className="flex items-center mt-2">
              {metrics.rmse_after < metrics.rmse_before ? (
                <>
                  <TrendingDown className="h-4 w-4 text-green-600 mr-1" />
                  <span className="text-sm text-green-600">
                    {((metrics.rmse_before - metrics.rmse_after) / metrics.rmse_before * 100).toFixed(1)}% improvement
                  </span>
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4 text-red-600 mr-1" />
                  <span className="text-sm text-red-600">
                    {((metrics.rmse_after - metrics.rmse_before) / metrics.rmse_before * 100).toFixed(1)}% degradation
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Claims Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-green-600">Improved:</span>
                <span className="font-semibold">{metrics.improved_count} ({((metrics.improved_count / metrics.total_claims) * 100).toFixed(1)}%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Unchanged:</span>
                <span className="font-semibold">{metrics.unchanged_count} ({((metrics.unchanged_count / metrics.total_claims) * 100).toFixed(1)}%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-red-600">Degraded:</span>
                <span className="font-semibold">{metrics.degraded_count} ({((metrics.degraded_count / metrics.total_claims) * 100).toFixed(1)}%)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Variance Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Variance Distribution: Before vs After</CardTitle>
          <CardDescription>Distribution of prediction errors across variance ranges</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={varianceDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="before" fill="#94a3b8" name="Before Recalibration" />
              <Bar dataKey="after" fill="#10b981" name="After Recalibration" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Prediction Scatter Plot */}
      <Card>
        <CardHeader>
          <CardTitle>Actual vs Predicted Values</CardTitle>
          <CardDescription>Comparison of predictions before and after recalibration</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="actual"
                name="Actual"
                label={{ value: 'Actual Value ($)', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="original"
                name="Predicted"
                label={{ value: 'Predicted Value ($)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <p className="font-semibold">{data.claim_id}</p>
                        <p className="text-sm">Actual: ${data.actual.toLocaleString()}</p>
                        <p className="text-sm">Original Pred: ${data.original.toLocaleString()}</p>
                        <p className="text-sm">Recalibrated: ${data.recalibrated.toLocaleString()}</p>
                        <p className="text-sm font-semibold">
                          Improvement: {data.improvement > 0 ? '+' : ''}{data.improvement.toFixed(1)}%
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Scatter name="Original Predictions" data={scatterData} fill="#94a3b8" opacity={0.6} />
              <Scatter name="Recalibrated Predictions" data={scatterData} dataKey="recalibrated" fill="#10b981" opacity={0.6} />
            </ScatterChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Top Improved Claims */}
      <Card>
        <CardHeader>
          <CardTitle>Top {showTopN} Most Improved Claims</CardTitle>
          <CardDescription>Claims with the greatest improvement in prediction accuracy</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Rank</th>
                  <th className="text-left p-2">Claim ID</th>
                  <th className="text-right p-2">Actual</th>
                  <th className="text-right p-2">Before</th>
                  <th className="text-right p-2">After</th>
                  <th className="text-right p-2">Variance Before</th>
                  <th className="text-right p-2">Variance After</th>
                  <th className="text-right p-2">Improvement</th>
                </tr>
              </thead>
              <tbody>
                {topImproved.map((result, index) => (
                  <tr key={result.claim_id} className="border-b hover:bg-gray-50">
                    <td className="p-2">{index + 1}</td>
                    <td className="p-2 font-medium">{result.claim_id}</td>
                    <td className="p-2 text-right">${result.actual_value.toLocaleString()}</td>
                    <td className="p-2 text-right">${result.original_prediction.toLocaleString()}</td>
                    <td className="p-2 text-right text-green-600 font-semibold">
                      ${result.recalibrated_prediction.toLocaleString()}
                    </td>
                    <td className="p-2 text-right">{result.original_variance_pct.toFixed(2)}%</td>
                    <td className="p-2 text-right text-green-600">{result.recalibrated_variance_pct.toFixed(2)}%</td>
                    <td className="p-2 text-right">
                      <Badge variant={result.improvement_pct > 0 ? 'default' : 'destructive'}>
                        {result.improvement_pct > 0 ? '+' : ''}{result.improvement_pct.toFixed(1)}%
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
