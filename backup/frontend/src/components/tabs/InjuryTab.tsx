import { ClaimData } from "@/types/claims";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid, Pie, PieChart, Cell } from "recharts";
import { useMemo } from "react";

interface InjuryTabProps {
  data: ClaimData[];
}

const COLORS = ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))', 'hsl(var(--chart-5))'];

export function InjuryTab({ data }: InjuryTabProps) {
  const injurySettlement = useMemo(() => {
    const groups: { [key: string]: { settlement: number; count: number } } = {};
    
    data.forEach(claim => {
      if (!groups[claim.INJURY_GROUP_CODE]) {
        groups[claim.INJURY_GROUP_CODE] = { settlement: 0, count: 0 };
      }
      groups[claim.INJURY_GROUP_CODE].settlement += claim.DOLLARAMOUNTHIGH;
      groups[claim.INJURY_GROUP_CODE].count += 1;
    });

    return Object.entries(groups)
      .map(([name, { settlement, count }]) => ({
        name,
        avgSettlement: settlement / count
      }))
      .sort((a, b) => b.avgSettlement - a.avgSettlement);
  }, [data]);

  const injuryVariance = useMemo(() => {
    const groups: { [key: string]: { variance: number; count: number } } = {};
    
    data.forEach(claim => {
      if (!groups[claim.INJURY_GROUP_CODE]) {
        groups[claim.INJURY_GROUP_CODE] = { variance: 0, count: 0 };
      }
      groups[claim.INJURY_GROUP_CODE].variance += Math.abs(claim.variance_pct);
      groups[claim.INJURY_GROUP_CODE].count += 1;
    });

    return Object.entries(groups)
      .map(([name, { variance, count }]) => ({
        name,
        avgVariance: variance / count
      }))
      .sort((a, b) => b.avgVariance - a.avgVariance);
  }, [data]);

  const injuryVolume = useMemo(() => {
    const groups: { [key: string]: number } = {};
    
    data.forEach(claim => {
      groups[claim.INJURY_GROUP_CODE] = (groups[claim.INJURY_GROUP_CODE] || 0) + 1;
    });

    return Object.entries(groups)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  return (
    <>
      <div className="bg-card rounded-xl p-6 border border-border shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Average Settlement by Injury Group</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={injurySettlement}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
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
            <Bar dataKey="avgSettlement" name="Avg Settlement" fill="hsl(var(--chart-1))" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-xl font-semibold mb-4">Variance by Injury Group</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={injuryVariance}>
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
              <Bar dataKey="avgVariance" name="Avg Variance (%)" fill="hsl(var(--chart-2))" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-xl font-semibold mb-4">Claims Volume by Injury Group</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={injuryVolume}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={(entry) => `${entry.name}: ${entry.value}`}
              >
                {injuryVolume.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
