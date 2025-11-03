import { ClaimData } from "@/types/claims";
import { Line, LineChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { useMemo } from "react";
import { KPICard } from "@/components/dashboard/KPICard";

interface AlignmentTabProps {
  data: ClaimData[];
}

export function AlignmentTab({ data }: AlignmentTabProps) {
  const kpis = useMemo(() => {
    const totalVariance = data.reduce((sum, claim) => sum + Math.abs(claim.variance_pct), 0);
    const avgVariance = totalVariance / data.length;
    const outsideThreshold = data.filter(claim => Math.abs(claim.variance_pct) > 25).length;
    const accuracy = ((data.length - outsideThreshold) / data.length) * 100;

    return {
      avgVariance: avgVariance.toFixed(1),
      outsideThreshold,
      accuracy: accuracy.toFixed(1)
    };
  }, [data]);

  const alignmentData = useMemo(() => {
    const monthly: { [key: string]: { consensus: number; model: number; count: number } } = {};
    
    data.forEach(claim => {
      const month = claim.claim_date.substring(0, 7);
      if (!monthly[month]) {
        monthly[month] = { consensus: 0, model: 0, count: 0 };
      }
      monthly[month].consensus += claim.DOLLARAMOUNTHIGH;
      monthly[month].model += claim.predicted_pain_suffering;
      monthly[month].count += 1;
    });

    return Object.entries(monthly)
      .map(([month, { consensus, model, count }]) => ({
        month,
        consensus: consensus / count,
        model: model / count
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [data]);

  const yoyData = useMemo(() => {
    const yearly: { [key: string]: { variance: number; settlement: number; count: number } } = {};
    
    data.forEach(claim => {
      const year = claim.claim_date.substring(0, 4);
      if (!yearly[year]) {
        yearly[year] = { variance: 0, settlement: 0, count: 0 };
      }
      yearly[year].variance += Math.abs(claim.variance_pct);
      yearly[year].settlement += claim.DOLLARAMOUNTHIGH;
      yearly[year].count += 1;
    });

    return Object.entries(yearly)
      .map(([year, { variance, settlement, count }]) => ({
        year,
        avgVariance: variance / count,
        avgSettlement: settlement / count
      }))
      .sort((a, b) => a.year.localeCompare(b.year));
  }, [data]);

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <KPICard
          title="Avg Model Variance"
          value={`${kpis.avgVariance}%`}
        />
        <KPICard
          title="Claims Outside Threshold"
          value={kpis.outsideThreshold}
        />
        <KPICard
          title="Model Accuracy"
          value={`${kpis.accuracy}%`}
        />
      </div>

      <div className="bg-card rounded-xl p-6 border border-border shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Consensus vs Model Alignment Over Time</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={alignmentData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
            <YAxis stroke="hsl(var(--muted-foreground))" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '0.5rem',
              }}
              formatter={(value: number) => `$${value.toLocaleString()}`}
            />
            <Legend />
            <Line type="monotone" dataKey="consensus" name="Consensus Settlement" stroke="hsl(var(--chart-1))" strokeWidth={2} />
            <Line type="monotone" dataKey="model" name="Model Prediction" stroke="hsl(var(--chart-2))" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-card rounded-xl p-6 border border-border shadow-md">
        <h3 className="text-xl font-semibold mb-4">Year-over-Year: Historical Comparisons</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={yoyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="year" stroke="hsl(var(--muted-foreground))" />
            <YAxis yAxisId="left" stroke="hsl(var(--muted-foreground))" />
            <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--muted-foreground))" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '0.5rem',
              }}
            />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="avgVariance" name="Avg Variance (%)" stroke="hsl(var(--chart-3))" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="avgSettlement" name="Avg Settlement ($)" stroke="hsl(var(--chart-4))" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
