import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { WeightConfig } from '../../types/claims';

interface FactorImpactChartProps {
  factorImpacts: Map<string, number>;
  weights: WeightConfig[];
  adjustedWeights: Map<string, number>;
}

const CATEGORY_COLORS = {
  Causation: '#3b82f6',
  Severity: '#ef4444',
  Treatment: '#10b981',
  Clinical: '#f59e0b',
  Disability: '#8b5cf6',
};

export default function FactorImpactChart({
  factorImpacts,
  weights,
  adjustedWeights,
}: FactorImpactChartProps) {
  const chartData = useMemo(() => {
    const data = Array.from(factorImpacts.entries())
      .map(([factorName, impact]) => {
        const weightConfig = weights.find((w) => w.factor_name === factorName);
        const currentWeight = adjustedWeights.get(factorName) || weightConfig?.base_weight || 0;

        return {
          name: factorName,
          impact: impact,
          weight: currentWeight,
          category: weightConfig?.category || 'Unknown',
          weightedImpact: impact * currentWeight,
        };
      })
      .sort((a, b) => b.weightedImpact - a.weightedImpact)
      .slice(0, 20); // Top 20 factors

    return data;
  }, [factorImpacts, weights, adjustedWeights]);

  const topFactorsData = useMemo(() => {
    return chartData.slice(0, 10);
  }, [chartData]);

  const categoryImpactData = useMemo(() => {
    const categoryMap = new Map<string, number>();

    chartData.forEach((item) => {
      const current = categoryMap.get(item.category) || 0;
      categoryMap.set(item.category, current + item.weightedImpact);
    });

    return Array.from(categoryMap.entries())
      .map(([category, impact]) => ({
        category,
        impact,
        color: CATEGORY_COLORS[category as keyof typeof CATEGORY_COLORS] || '#6b7280',
      }))
      .sort((a, b) => b.impact - a.impact);
  }, [chartData]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Top Individual Factors */}
      <Card>
        <CardHeader>
          <CardTitle>Top 10 Factor Impact</CardTitle>
          <CardDescription>
            Factors with highest weighted impact on variance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={topFactorsData} layout="vertical" margin={{ left: 150 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 12 }} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <p className="font-semibold">{data.name}</p>
                        <p className="text-sm text-muted-foreground">{data.category}</p>
                        <p className="text-sm">Impact: {data.impact.toFixed(2)}</p>
                        <p className="text-sm">Weight: {data.weight.toFixed(3)}</p>
                        <p className="text-sm font-semibold">
                          Weighted Impact: {data.weightedImpact.toFixed(2)}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="weightedImpact" name="Weighted Impact">
                {topFactorsData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={CATEGORY_COLORS[entry.category as keyof typeof CATEGORY_COLORS] || '#6b7280'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Impact by Category */}
      <Card>
        <CardHeader>
          <CardTitle>Impact by Category</CardTitle>
          <CardDescription>
            Aggregate impact grouped by factor category
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={categoryImpactData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <p className="font-semibold">{data.category}</p>
                        <p className="text-sm">Total Impact: {data.impact.toFixed(2)}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="impact" name="Total Impact">
                {categoryImpactData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Detailed Factor Table */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>All Factors Impact Analysis</CardTitle>
          <CardDescription>Comprehensive view of all factor impacts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Rank</th>
                  <th className="text-left p-2">Factor</th>
                  <th className="text-left p-2">Category</th>
                  <th className="text-right p-2">Impact</th>
                  <th className="text-right p-2">Weight</th>
                  <th className="text-right p-2">Weighted Impact</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={item.name} className="border-b hover:bg-gray-50">
                    <td className="p-2">{index + 1}</td>
                    <td className="p-2 font-medium">{item.name}</td>
                    <td className="p-2">
                      <span
                        className="px-2 py-1 rounded text-xs font-semibold text-white"
                        style={{
                          backgroundColor: CATEGORY_COLORS[item.category as keyof typeof CATEGORY_COLORS] || '#6b7280',
                        }}
                      >
                        {item.category}
                      </span>
                    </td>
                    <td className="p-2 text-right">{item.impact.toFixed(2)}</td>
                    <td className="p-2 text-right">{item.weight.toFixed(3)}</td>
                    <td className="p-2 text-right font-semibold">{item.weightedImpact.toFixed(2)}</td>
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
