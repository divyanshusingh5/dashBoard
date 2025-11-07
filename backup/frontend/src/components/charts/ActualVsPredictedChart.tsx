import { ClaimData } from "@/types/claims";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from "recharts";

interface ActualVsPredictedChartProps {
  data: ClaimData[];
}

export function ActualVsPredictedChart({ data }: ActualVsPredictedChartProps) {
  const monthlyData: { [key: string]: { actual: number; predicted: number; count: number } } = {};
  
  data.forEach(d => {
    const month = d.claim_date.substring(0, 7);
    if (!monthlyData[month]) {
      monthlyData[month] = { actual: 0, predicted: 0, count: 0 };
    }
    monthlyData[month].actual += d.DOLLARAMOUNTHIGH;
    monthlyData[month].predicted += d.predicted_pain_suffering;
    monthlyData[month].count++;
  });
  
  const chartData = Object.keys(monthlyData)
    .sort()
    .map(month => ({
      month,
      actual: Math.round(monthlyData[month].actual / monthlyData[month].count),
      predicted: Math.round(monthlyData[month].predicted / monthlyData[month].count)
    }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--chart-2))" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0.1}/>
          </linearGradient>
          <linearGradient id="predictedGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--chart-3))" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="hsl(var(--chart-3))" stopOpacity={0.1}/>
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
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '0.75rem',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          }}
          formatter={(value: number) => `$${value.toLocaleString()}`}
        />
        <Legend />
        <Area
          type="monotone" 
          dataKey="actual" 
          name="Actual Settlement"
          stroke="hsl(var(--chart-2))" 
          strokeWidth={2}
          fill="url(#actualGradient)"
          activeDot={{ r: 6, strokeWidth: 2 }}
        />
        <Area
          type="monotone" 
          dataKey="predicted" 
          name="Predicted Settlement"
          stroke="hsl(var(--chart-3))" 
          strokeWidth={2}
          fill="url(#predictedGradient)"
          activeDot={{ r: 6, strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
