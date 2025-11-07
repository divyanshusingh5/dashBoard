import { ClaimData } from "@/types/claims";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { ImprovedRegionalTrendsChart } from "@/components/charts/ImprovedRegionalTrendsChart";

interface VenueTabProps {
  data: ClaimData[];
}

type MetricType = 'settlement' | 'variance' | 'claims';

export function VenueTab({ data }: VenueTabProps) {
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('settlement');

  const venueSettlement = useMemo(() => {
    const states: { [key: string]: { settlement: number; count: number } } = {};
    
    data.forEach(claim => {
      if (!states[claim.VENUESTATE]) {
        states[claim.VENUESTATE] = { settlement: 0, count: 0 };
      }
      states[claim.VENUESTATE].settlement += claim.DOLLARAMOUNTHIGH;
      states[claim.VENUESTATE].count += 1;
    });

    return Object.entries(states)
      .map(([name, { settlement, count }]) => ({
        name,
        avgSettlement: settlement / count
      }))
      .sort((a, b) => b.avgSettlement - a.avgSettlement);
  }, [data]);

  const venueVolume = useMemo(() => {
    const states: { [key: string]: number } = {};
    
    data.forEach(claim => {
      states[claim.VENUESTATE] = (states[claim.VENUESTATE] || 0) + 1;
    });

    return Object.entries(states)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  const countyPerformance = useMemo(() => {
    const counties: { [key: string]: { variance: number; count: number } } = {};
    
    data.forEach(claim => {
      if (!counties[claim.COUNTYNAME]) {
        counties[claim.COUNTYNAME] = { variance: 0, count: 0 };
      }
      counties[claim.COUNTYNAME].variance += Math.abs(claim.variance_pct);
      counties[claim.COUNTYNAME].count += 1;
    });

    return Object.entries(counties)
      .map(([name, { variance, count }]) => ({
        name,
        avgVariance: variance / count
      }))
      .sort((a, b) => b.avgVariance - a.avgVariance);
  }, [data]);


  const venueRiskHeatmap = useMemo(() => {
    const counties: { [key: string]: { variance: number; count: number; settlement: number } } = {};
    
    data.forEach(claim => {
      if (!counties[claim.COUNTYNAME]) {
        counties[claim.COUNTYNAME] = { variance: 0, count: 0, settlement: 0 };
      }
      counties[claim.COUNTYNAME].variance += Math.abs(claim.variance_pct);
      counties[claim.COUNTYNAME].count += 1;
      counties[claim.COUNTYNAME].settlement += claim.DOLLARAMOUNTHIGH;
    });

    return Object.entries(counties)
      .map(([name, { variance, count, settlement }]) => ({
        name,
        riskScore: (variance / count) * (settlement / count / 10000)
      }))
      .sort((a, b) => b.riskScore - a.riskScore)
      .slice(0, 10);
  }, [data]);

  return (
    <>
      <div className="bg-card rounded-xl p-6 border border-border shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Average Settlement by State (Venue)</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={venueSettlement}>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-xl font-semibold mb-4">Claims Volume by State</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={venueVolume}>
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
              <Bar dataKey="value" name="Claims" fill="hsl(var(--chart-2))" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-xl font-semibold mb-4">County Performance Map</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={countyPerformance}>
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
              <Bar dataKey="avgVariance" name="Avg Variance (%)" fill="hsl(var(--chart-3))" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-card rounded-xl p-6 border border-border shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Regional Trends: State Performance Analysis</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Track how different states perform over time across key metrics
        </p>
        <div className="flex gap-2 mb-6 flex-wrap">
          <button
            onClick={() => setSelectedMetric('settlement')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-sm",
              selectedMetric === 'settlement'
                ? 'bg-primary text-primary-foreground shadow-primary/20'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            💰 Settlement Amount
          </button>
          <button
            onClick={() => setSelectedMetric('variance')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-sm",
              selectedMetric === 'variance'
                ? 'bg-primary text-primary-foreground shadow-primary/20'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            📊 Variance Rate
          </button>
          <button
            onClick={() => setSelectedMetric('claims')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-sm",
              selectedMetric === 'claims'
                ? 'bg-primary text-primary-foreground shadow-primary/20'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            📈 Claims Volume
          </button>
        </div>
        <ImprovedRegionalTrendsChart data={data} metric={selectedMetric} />
      </div>

      <div className="bg-card rounded-xl p-6 border border-border shadow-md">
        <h3 className="text-xl font-semibold mb-4">Venue Risk Heatmap: High Variance Counties</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={venueRiskHeatmap}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
            <YAxis stroke="hsl(var(--muted-foreground))" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '0.5rem',
              }}
              formatter={(value: number) => `Risk Score: ${value.toFixed(1)}`}
            />
            <Legend />
            <Bar dataKey="riskScore" name="Risk Score" fill="hsl(var(--chart-5))" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
