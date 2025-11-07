import { ClaimData } from "@/types/claims";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from "recharts";

interface VarianceTrendChartProps {
  data: ClaimData[];
}

export function VarianceTrendChart({ data }: VarianceTrendChartProps) {
  const monthlyData: { [key: string]: { count: number; sumVariance: number } } = {};
  
  data.forEach(d => {
    const month = d.claim_date.substring(0, 7);
    if (!monthlyData[month]) {
      monthlyData[month] = { count: 0, sumVariance: 0 };
    }
    monthlyData[month].count++;
    monthlyData[month].sumVariance += Math.abs(d.variance_pct);
  });
  
  const chartData = Object.keys(monthlyData)
    .sort()
    .map(month => ({
      month,
      variance: parseFloat((monthlyData[month].sumVariance / monthlyData[month].count).toFixed(1))
    }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id="varianceGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0.1}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
        <XAxis 
          dataKey="month" 
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <YAxis 
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '0.75rem',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          }}
          formatter={(value: number) => `${value.toFixed(1)}%`}
        />
        <Legend />
        <Area
          type="monotone" 
          dataKey="variance" 
          name="Avg Variance %"
          stroke="hsl(var(--chart-1))" 
          strokeWidth={2}
          fill="url(#varianceGradient)"
          activeDot={{ r: 6, strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
