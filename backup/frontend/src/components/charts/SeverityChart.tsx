import { ClaimData } from "@/types/claims";
import { Pie, PieChart, ResponsiveContainer, Cell, Legend, Tooltip } from "recharts";

interface SeverityChartProps {
  data: ClaimData[];
}

const COLORS = ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))'];

export function SeverityChart({ data }: SeverityChartProps) {
const severityRanges: { [key: string]: number } = { 
    'Low (1-4)': 0, 
    'Medium (4-8)': 0, 
    'High (8+)': 0 
  };
  
  data.forEach(d => {
    if (d.SEVERITY_SCORE <= 4) severityRanges['Low (1-4)']++;
    else if (d.SEVERITY_SCORE <= 8) severityRanges['Medium (4-8)']++;
    else severityRanges['High (8+)']++;
  });
  
  const chartData = Object.entries(severityRanges).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
          label={(entry) => `${entry.name}: ${entry.value}`}
        >
          {chartData.map((entry, index) => (
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
  );
}
