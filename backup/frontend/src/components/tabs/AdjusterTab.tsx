import { ClaimData } from "@/types/claims";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { useMemo } from "react";

interface AdjusterTabProps {
  data: ClaimData[];
}

export function AdjusterTab({ data }: AdjusterTabProps) {
  const adjusterVariance = useMemo(() => {
    const adjusters: { [key: string]: { variance: number; count: number } } = {};
    
    data.forEach(claim => {
      if (!adjusters[claim.adjuster]) {
        adjusters[claim.adjuster] = { variance: 0, count: 0 };
      }
      adjusters[claim.adjuster].variance += Math.abs(claim.variance_pct);
      adjusters[claim.adjuster].count += 1;
    });

    return Object.entries(adjusters)
      .map(([name, { variance, count }]) => ({
        name,
        avgVariance: variance / count
      }))
      .sort((a, b) => b.avgVariance - a.avgVariance);
  }, [data]);

  const adjusterVolume = useMemo(() => {
    const adjusters: { [key: string]: number } = {};
    
    data.forEach(claim => {
      adjusters[claim.adjuster] = (adjusters[claim.adjuster] || 0) + 1;
    });

    return Object.entries(adjusters)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  const adjusterDays = useMemo(() => {
    const adjusters: { [key: string]: { days: number; count: number } } = {};
    
    data.forEach(claim => {
      if (!adjusters[claim.adjuster]) {
        adjusters[claim.adjuster] = { days: 0, count: 0 };
      }
      adjusters[claim.adjuster].days += claim.SETTLEMENT_DAYS;
      adjusters[claim.adjuster].count += 1;
    });

    return Object.entries(adjusters)
      .map(([name, { days, count }]) => ({
        name,
        avgDays: days / count
      }))
      .sort((a, b) => a.avgDays - b.avgDays);
  }, [data]);

  return (
    <>
      <div className="bg-card rounded-xl p-6 border border-border shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Adjuster Performance: Model Variance</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={adjusterVariance}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
            <YAxis stroke="hsl(var(--muted-foreground))" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '0.5rem',
              }}
              formatter={(value: number) => `${value.toFixed(1)}%`}
            />
            <Legend />
            <Bar dataKey="avgVariance" name="Avg Variance (%)" fill="hsl(var(--chart-1))" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-xl font-semibold mb-4">Claims Volume by Adjuster</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={adjusterVolume}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Bar dataKey="value" name="Claims Handled" fill="hsl(var(--chart-2))" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-xl font-semibold mb-4">Avg Days to Settlement</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={adjusterDays}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
                formatter={(value: number) => `${value.toFixed(0)} days`}
              />
              <Legend />
              <Bar dataKey="avgDays" name="Avg Days" fill="hsl(var(--chart-3))" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
