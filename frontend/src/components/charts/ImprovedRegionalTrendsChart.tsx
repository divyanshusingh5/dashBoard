import { ClaimData } from "@/types/claims";
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { useMemo } from "react";

interface ImprovedRegionalTrendsChartProps {
  data: ClaimData[];
  metric: 'settlement' | 'variance' | 'claims';
}

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))'
];

export function ImprovedRegionalTrendsChart({ data, metric }: ImprovedRegionalTrendsChartProps) {
  const chartData = useMemo(() => {
    const monthly: { [key: string]: { [state: string]: { value: number; count: number } } } = {};
    
    data.forEach(claim => {
      const month = claim.claim_date.substring(0, 7);
      if (!monthly[month]) {
        monthly[month] = {};
      }
      if (!monthly[month][claim.VENUESTATE]) {
        monthly[month][claim.VENUESTATE] = { value: 0, count: 0 };
      }
      
      if (metric === 'settlement') {
        monthly[month][claim.VENUESTATE].value += claim.DOLLARAMOUNTHIGH;
      } else if (metric === 'variance') {
        monthly[month][claim.VENUESTATE].value += Math.abs(claim.variance_pct);
      } else {
        monthly[month][claim.VENUESTATE].value += 1;
      }
      monthly[month][claim.VENUESTATE].count += 1;
    });

    const states = [...new Set(data.map(d => d.VENUESTATE))].slice(0, 5);
    
    return Object.entries(monthly)
      .map(([month, stateData]) => {
        const result: any = { month };
        states.forEach(state => {
          if (stateData[state]) {
            result[state] = metric === 'claims' 
              ? stateData[state].value 
              : stateData[state].value / stateData[state].count;
          }
        });
        return result;
      })
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [data, metric]);

  const states = useMemo(() => [...new Set(data.map(d => d.VENUESTATE))].slice(0, 5), [data]);

  const formatValue = (value: number) => {
    if (metric === 'settlement') {
      return `$${value.toLocaleString()}`;
    } else if (metric === 'variance') {
      return `${value.toFixed(1)}%`;
    }
    return value.toString();
  };

  return (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={chartData}>
        <defs>
          {states.map((state, idx) => (
            <linearGradient key={state} id={`gradient-${state}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS[idx % COLORS.length]} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={COLORS[idx % COLORS.length]} stopOpacity={0.1}/>
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
        <XAxis 
          dataKey="month" 
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <YAxis 
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '0.75rem',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          }}
          formatter={(value: number) => formatValue(value)}
        />
        <Legend 
          wrapperStyle={{
            paddingTop: '20px'
          }}
        />
        {states.map((state, idx) => (
          <Area
            key={state}
            type="monotone"
            dataKey={state}
            stroke={COLORS[idx % COLORS.length]}
            strokeWidth={2}
            fill={`url(#gradient-${state})`}
            activeDot={{ r: 6, strokeWidth: 2 }}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
}
