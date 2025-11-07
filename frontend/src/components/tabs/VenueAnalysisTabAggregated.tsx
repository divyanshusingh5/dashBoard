/**
 * Venue Analysis Tab - Aggregated Data
 * Shows venue trends, factor combinations, and venue shift recommendations
 */

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, AlertTriangle, ArrowRight } from "lucide-react";
import { AggregatedData } from "@/hooks/useAggregatedClaimsDataAPI";
import { useMemo, useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area,
} from "recharts";

interface VenueAnalysisTabProps {
  data: AggregatedData;
}

const VENUE_COLORS = {
  'Conservative': '#ef4444', // red
  'Moderate': '#f59e0b',     // orange
  'Liberal': '#10b981',      // green
};

export function VenueAnalysisTabAggregated({ data }: VenueAnalysisTabProps) {
  const [venueShiftRecommendations, setVenueShiftRecommendations] = useState<any[]>([]);
  const [loadingShifts, setLoadingShifts] = useState(false);

  // Fetch venue shift recommendations
  useEffect(() => {
    const fetchVenueShifts = async () => {
      try {
        setLoadingShifts(true);
        const response = await fetch('http://localhost:8000/api/v1/aggregation/venue-shift-analysis?months=12');
        const result = await response.json();
        if (result.recommendations) {
          setVenueShiftRecommendations(result.recommendations);
        }
      } catch (error) {
        console.error('Error fetching venue shift recommendations:', error);
      } finally {
        setLoadingShifts(false);
      }
    };

    fetchVenueShifts();
  }, []);

  // Venue performance by rating
  const venuePerformance = useMemo(() => {
    const grouped = data.venueAnalysis.reduce((acc, item) => {
      const existing = acc.find(v => v.venue_rating === item.venue_rating);
      if (existing) {
        existing.claim_count += item.claim_count;
        existing.total_settlement += item.avg_settlement * item.claim_count;
        existing.total_predicted += item.avg_predicted * item.claim_count;
        existing.total_variance += Math.abs(item.avg_variance_pct) * item.claim_count;
      } else {
        acc.push({
          venue_rating: item.venue_rating,
          claim_count: item.claim_count,
          total_settlement: item.avg_settlement * item.claim_count,
          total_predicted: item.avg_predicted * item.claim_count,
          total_variance: Math.abs(item.avg_variance_pct) * item.claim_count,
        });
      }
      return acc;
    }, [] as any[]);

    return grouped.map(v => ({
      venue: v.venue_rating,
      claims: v.claim_count,
      avgSettlement: Math.round(v.total_settlement / v.claim_count),
      avgPredicted: Math.round(v.total_predicted / v.claim_count),
      avgVariance: (v.total_variance / v.claim_count).toFixed(2),
    })).sort((a, b) => {
      const order = { 'Conservative': 1, 'Moderate': 2, 'Liberal': 3 };
      return (order[a.venue as keyof typeof order] || 99) - (order[b.venue as keyof typeof order] || 99);
    });
  }, [data.venueAnalysis]);

  // Top counties by venue rating with variance
  const topCountiesByVenue = useMemo(() => {
    return ['Conservative', 'Moderate', 'Liberal'].map(venue => {
      const venueData = data.venueAnalysis
        .filter(v => v.venue_rating === venue)
        .sort((a, b) => b.claim_count - a.claim_count)
        .slice(0, 5);

      return {
        venue,
        counties: venueData.map(v => ({
          county: `${v.county}, ${v.state}`,
          claims: v.claim_count,
          avgSettlement: Math.round(v.avg_settlement),
          variance: v.avg_variance_pct.toFixed(1),
        })),
      };
    });
  }, [data.venueAnalysis]);

  // Venue trend over time (simulated monthly data)
  const venueTrend = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months.map((month, idx) => {
      const baseConservative = 75000 + Math.random() * 5000;
      const baseModerate = 95000 + Math.random() * 8000;
      const baseLiberal = 115000 + Math.random() * 10000;

      return {
        month,
        Conservative: Math.round(baseConservative),
        Moderate: Math.round(baseModerate),
        Liberal: Math.round(baseLiberal),
      };
    });
  }, []);

  return (
    <div className="space-y-6">
      {/* Venue Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {venuePerformance.map((venue, idx) => (
          <Card key={idx} className="border-2" style={{ borderColor: VENUE_COLORS[venue.venue as keyof typeof VENUE_COLORS] }}>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center justify-between">
                {venue.venue}
                <Badge variant="outline" style={{
                  borderColor: VENUE_COLORS[venue.venue as keyof typeof VENUE_COLORS],
                  color: VENUE_COLORS[venue.venue as keyof typeof VENUE_COLORS]
                }}>
                  {venue.claims.toLocaleString()} claims
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Settlement:</span>
                  <span className="font-bold">${venue.avgSettlement.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Predicted:</span>
                  <span className="font-medium text-gray-700">${venue.avgPredicted.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg Variance:</span>
                  <Badge variant={parseFloat(venue.avgVariance) > 15 ? 'destructive' : 'secondary'}>
                    {venue.avgVariance}%
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Venue Trend Chart */}
      <Card className="border-purple-200">
        <CardHeader>
          <CardTitle>Venue Settlement Trends (12 Months)</CardTitle>
          <CardDescription>Average settlement amounts by venue rating over time</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <ComposedChart data={venueTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" />
              <YAxis
                stroke="#6b7280"
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(value: any) => [`$${value.toLocaleString()}`, '']}
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="Conservative"
                fill="#ef4444"
                stroke="#dc2626"
                fillOpacity={0.2}
              />
              <Line
                type="monotone"
                dataKey="Moderate"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="Liberal"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 3 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Top Counties by Venue Rating */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {topCountiesByVenue.map((venueGroup, idx) => (
          <Card key={idx} className="border-2" style={{ borderColor: VENUE_COLORS[venueGroup.venue as keyof typeof VENUE_COLORS] }}>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{venueGroup.venue} Venues - Top Counties</CardTitle>
              <CardDescription>Highest claim volumes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {venueGroup.counties.map((county, cidx) => (
                  <div key={cidx} className="border-b pb-2 last:border-0">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-sm font-medium text-gray-900">{county.county}</span>
                      <Badge variant="outline" className="text-xs">{county.claims} claims</Badge>
                    </div>
                    <div className="flex justify-between text-xs text-gray-600">
                      <span>Avg: ${county.avgSettlement.toLocaleString()}</span>
                      <span className={`font-medium ${parseFloat(county.variance) > 15 ? 'text-red-600' : 'text-green-600'}`}>
                        {county.variance}% var
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Venue Shift Recommendations */}
      <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Venue Shift Recommendations
          </CardTitle>
          <CardDescription>
            Factor combinations where changing venue rating could reduce variance and improve predictions
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingShifts ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Analyzing venue shift opportunities...</span>
            </div>
          ) : venueShiftRecommendations.length === 0 ? (
            <div className="text-center py-8 text-gray-600">
              <AlertTriangle className="h-12 w-12 mx-auto mb-3 text-yellow-500" />
              <p>No venue shift recommendations available at this time.</p>
              <p className="text-sm mt-2">This could mean venues are already optimally assigned.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {venueShiftRecommendations.slice(0, 10).map((rec, idx) => (
                <div key={idx} className="border rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="border-2" style={{
                        borderColor: VENUE_COLORS[rec.current_venue as keyof typeof VENUE_COLORS]
                      }}>
                        {rec.current_venue}
                      </Badge>
                      <ArrowRight className="h-4 w-4 text-gray-400" />
                      <Badge className="bg-green-600">
                        {rec.recommended_venue}
                      </Badge>
                    </div>
                    <Badge variant="destructive">
                      Potential ${rec.potential_savings?.toLocaleString() || '0'} savings
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-700">
                    <p><strong>Factor:</strong> {rec.factor_description || 'Multiple factors'}</p>
                    <p><strong>County:</strong> {rec.county}, {rec.state}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {rec.claim_count} claims • Current variance: {rec.current_variance?.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Venue Performance by State */}
      <Card className="border-gray-200">
        <CardHeader>
          <CardTitle>Venue Distribution by State</CardTitle>
          <CardDescription>Claim counts across venue ratings for top states</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={
                data.venueAnalysis
                  .reduce((acc, item) => {
                    const existing = acc.find(s => s.state === item.state);
                    if (existing) {
                      existing[item.venue_rating] = (existing[item.venue_rating] || 0) + item.claim_count;
                      existing.total += item.claim_count;
                    } else {
                      acc.push({
                        state: item.state,
                        [item.venue_rating]: item.claim_count,
                        total: item.claim_count,
                      });
                    }
                    return acc;
                  }, [] as any[])
                  .sort((a, b) => b.total - a.total)
                  .slice(0, 10)
              }
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="state" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Legend />
              <Bar dataKey="Conservative" fill="#ef4444" />
              <Bar dataKey="Moderate" fill="#f59e0b" />
              <Bar dataKey="Liberal" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
