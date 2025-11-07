import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AggregatedData } from "@/hooks/useAggregatedClaimsData";
import { useMemo } from "react";
import { Users, TrendingDown, TrendingUp, Clock, DollarSign } from "lucide-react";

interface AdjusterPerformanceTabAggregatedProps {
  data: AggregatedData | null;
}

export function AdjusterPerformanceTabAggregated({ data }: AdjusterPerformanceTabAggregatedProps) {
  if (!data) {
    return (
      <div className="p-8 text-center">
        <p className="text-muted-foreground">Loading adjuster performance...</p>
      </div>
    );
  }

  // Calculate overall metrics
  const overallMetrics = useMemo(() => {
    if (!data.adjusterPerformance || data.adjusterPerformance.length === 0) {
      return {
        totalClaims: 0,
        avgSettlement: 0,
        avgVariance: 0,
        avgDays: 0,
        highVariancePct: 0,
      };
    }

    const totalClaims = data.adjusterPerformance.reduce((sum, adj) => sum + (adj.claim_count || 0), 0);
    const totalSettlement = data.adjusterPerformance.reduce((sum, adj) =>
      sum + ((adj.avg_actual_settlement || 0) * (adj.claim_count || 0)), 0);
    const weightedVariance = data.adjusterPerformance.reduce((sum, adj) =>
      sum + ((adj.avg_variance_pct || 0) * (adj.claim_count || 0)), 0);
    const weightedDays = data.adjusterPerformance.reduce((sum, adj) =>
      sum + ((adj.avg_settlement_days || 0) * (adj.claim_count || 0)), 0);
    const totalHighVariance = data.adjusterPerformance.reduce((sum, adj) =>
      sum + (adj.high_variance_count || 0), 0);

    return {
      totalClaims,
      avgSettlement: totalClaims > 0 ? totalSettlement / totalClaims : 0,
      avgVariance: totalClaims > 0 ? weightedVariance / totalClaims : 0,
      avgDays: totalClaims > 0 ? weightedDays / totalClaims : 0,
      highVariancePct: totalClaims > 0 ? (totalHighVariance / totalClaims) * 100 : 0,
    };
  }, [data]);

  // Rank adjusters by various metrics
  const adjusterRankings = useMemo(() => {
    // Create separate copies to avoid mutation issues
    return {
      byVolume: [...data.adjusterPerformance].sort((a, b) => b.claim_count - a.claim_count),
      byLowVariance: [...data.adjusterPerformance].sort((a, b) => Math.abs(a.avg_variance_pct) - Math.abs(b.avg_variance_pct)),
      byHighVariance: [...data.adjusterPerformance].sort((a, b) => Math.abs(b.avg_variance_pct) - Math.abs(a.avg_variance_pct)),
      bySpeed: [...data.adjusterPerformance].sort((a, b) => a.avg_settlement_days - b.avg_settlement_days),
      bySlowest: [...data.adjusterPerformance].sort((a, b) => b.avg_settlement_days - a.avg_settlement_days),
    };
  }, [data]);

  // Find best performers for different injury groups
  const injuryGroupRecommendations = useMemo(() => {
    if (!data.injuryGroup || data.injuryGroup.length === 0) {
      return [];
    }

    // Get unique injury groups
    const injuryGroups = [...new Set(data.injuryGroup.map(i => i.injury_group).filter(Boolean))];

    // For each injury group, recommend adjusters with low variance in similar cases
    return injuryGroups.slice(0, 5).map(group => {
      const groupData = data.injuryGroup.filter(i => i.injury_group === group);
      const totalClaims = groupData.reduce((sum: number, i: typeof data.injuryGroup[0]) =>
        sum + (i.claim_count || 0), 0);
      const weightedVariance = groupData.reduce((sum: number, i: typeof data.injuryGroup[0]) =>
        sum + ((i.avg_variance_pct || 0) * (i.claim_count || 0)), 0);
      const avgGroupVariance = totalClaims > 0 ? weightedVariance / totalClaims : 0;

      // Find adjusters performing better than group average
      // Note: This is a simplified recommendation. In production, you'd want
      // adjuster-specific injury group data
      const recommendedAdjusters = adjusterRankings.byLowVariance
        .filter(adj => Math.abs(adj.avg_variance_pct || 0) < Math.abs(avgGroupVariance))
        .slice(0, 3);

      return {
        injuryGroup: group,
        avgVariance: avgGroupVariance,
        claimCount: totalClaims,
        recommendedAdjusters,
      };
    });
  }, [data, adjusterRankings]);

  // Identify over/under prediction patterns
  const predictionPatterns = useMemo(() => {
    return data.adjusterPerformance.map(adj => {
      const overpredictionRate = (adj.overprediction_count / adj.claim_count) * 100;
      const underpredictionRate = (adj.underprediction_count / adj.claim_count) * 100;

      let pattern = 'Balanced';
      if (overpredictionRate > 60) pattern = 'Over-Predicting';
      else if (underpredictionRate > 60) pattern = 'Under-Predicting';

      return {
        ...adj,
        overpredictionRate,
        underpredictionRate,
        pattern,
      };
    });
  }, [data]);

  // Top performers (low variance + high volume)
  const topPerformers = useMemo(() => {
    return [...data.adjusterPerformance]
      .filter(adj => adj.claim_count >= 10) // Minimum volume threshold
      .sort((a, b) => {
        // Score = low variance + high volume
        const scoreA = (1 / (Math.abs(a.avg_variance_pct) + 1)) * Math.log(a.claim_count);
        const scoreB = (1 / (Math.abs(b.avg_variance_pct) + 1)) * Math.log(b.claim_count);
        return scoreB - scoreA;
      })
      .slice(0, 5);
  }, [data]);

  return (
    <div className="space-y-6 p-6">
      {/* Overall Performance Alert */}
      <Alert className="border-blue-500 bg-blue-50">
        <Users className="h-4 w-4 text-blue-600" />
        <AlertTitle className="text-blue-900">Adjuster Performance Summary</AlertTitle>
        <AlertDescription className="text-blue-800">
          Tracking {data.adjusterPerformance.length} adjuster(s) managing {overallMetrics.totalClaims.toLocaleString()} claims
          with an average variance of {overallMetrics.avgVariance.toFixed(2)}% and {overallMetrics.avgDays.toFixed(0)} day settlement time.
        </AlertDescription>
      </Alert>

      {/* Key Metrics */}
      <div className="grid md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Users className="h-4 w-4" />
              Total Adjusters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.adjusterPerformance.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Avg Settlement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${Math.round(overallMetrics.avgSettlement).toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Variance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallMetrics.avgVariance.toFixed(2)}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Avg Days
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(overallMetrics.avgDays)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">High Variance %</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallMetrics.highVariancePct.toFixed(1)}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Top Performers */}
      <Card className="border-green-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-700">
            <TrendingDown className="h-5 w-5" />
            Top Performing Adjusters
          </CardTitle>
          <CardDescription>
            Adjusters with best combination of low variance and high claim volume
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topPerformers.map((adj, idx) => (
              <div key={idx} className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="font-semibold text-green-900 flex items-center gap-2">
                      <Badge className="bg-green-600">#{idx + 1}</Badge>
                      {adj.adjuster_name}
                    </div>
                    <p className="text-sm text-green-700 mt-1">
                      {adj.claim_count} claims • {adj.avg_variance_pct.toFixed(2)}% variance • {adj.avg_settlement_days} days avg
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Avg Settlement</div>
                    <div className="font-bold text-green-700">${Math.round(adj.avg_actual_settlement).toLocaleString()}</div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 mt-3 text-xs">
                  <div className="bg-white p-2 rounded">
                    <span className="text-muted-foreground">High Variance:</span>
                    <strong className="ml-1">{adj.high_variance_pct.toFixed(1)}%</strong>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <span className="text-muted-foreground">Over-predicted:</span>
                    <strong className="ml-1">{adj.overprediction_count}</strong>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <span className="text-muted-foreground">Under-predicted:</span>
                    <strong className="ml-1">{adj.underprediction_count}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Adjuster Recommendations by Injury Group */}
      <Card>
        <CardHeader>
          <CardTitle>Adjuster Assignment Recommendations by Injury Type</CardTitle>
          <CardDescription>
            Suggested adjusters for different injury groups based on variance performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {injuryGroupRecommendations.map((rec, idx) => (
              <div key={idx} className="p-4 bg-gray-50 rounded-lg border">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-semibold text-lg">{rec.injuryGroup} Injuries</h4>
                    <p className="text-sm text-muted-foreground">
                      {rec.claimCount} claims • {rec.avgVariance.toFixed(2)}% avg variance
                    </p>
                  </div>
                </div>
                <div className="mt-3">
                  <p className="text-sm font-medium mb-2">Recommended Adjusters (Lower variance than group average):</p>
                  <div className="grid md:grid-cols-3 gap-3">
                    {rec.recommendedAdjusters.length > 0 ? (
                      rec.recommendedAdjusters.map((adj, adjIdx) => (
                        <div key={adjIdx} className="p-3 bg-white rounded border">
                          <div className="font-semibold text-sm">{adj.adjuster_name}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {adj.claim_count} claims • {adj.avg_variance_pct.toFixed(2)}% variance
                          </div>
                          <Badge variant="outline" className="mt-2 text-xs">
                            {Math.abs(rec.avgVariance - adj.avg_variance_pct).toFixed(1)}% better
                          </Badge>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground col-span-3">
                        No adjusters currently performing better than group average. Consider training opportunities.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Rankings */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* By Volume */}
        <Card>
          <CardHeader>
            <CardTitle>Highest Claim Volume</CardTitle>
            <CardDescription>Adjusters handling the most claims</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {adjusterRankings.byVolume.slice(0, 5).map((adj, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{idx + 1}</Badge>
                    <span className="font-medium">{adj.adjuster_name}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">{adj.claim_count.toLocaleString()}</div>
                    <div className="text-xs text-muted-foreground">{adj.avg_variance_pct.toFixed(1)}% var</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* By Speed */}
        <Card>
          <CardHeader>
            <CardTitle>Fastest Settlement Times</CardTitle>
            <CardDescription>Adjusters with shortest average processing days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {adjusterRankings.bySpeed.slice(0, 5).map((adj, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{idx + 1}</Badge>
                    <span className="font-medium">{adj.adjuster_name}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-bold flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {Math.round(adj.avg_settlement_days)} days
                    </div>
                    <div className="text-xs text-muted-foreground">{adj.claim_count} claims</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Prediction Pattern Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Over/Under Prediction Patterns</CardTitle>
          <CardDescription>
            Identifying systematic over or under-prediction tendencies by adjuster
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Adjuster</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">Over-Predicted</th>
                  <th className="text-right p-2">Under-Predicted</th>
                  <th className="text-center p-2">Pattern</th>
                  <th className="text-right p-2">Avg Variance</th>
                </tr>
              </thead>
              <tbody>
                {predictionPatterns.map((adj, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{adj.adjuster_name}</td>
                    <td className="p-2 text-right">{adj.claim_count}</td>
                    <td className="p-2 text-right">
                      <span className="text-blue-600">{adj.overprediction_count} ({adj.overpredictionRate.toFixed(0)}%)</span>
                    </td>
                    <td className="p-2 text-right">
                      <span className="text-orange-600">{adj.underprediction_count} ({adj.underpredictionRate.toFixed(0)}%)</span>
                    </td>
                    <td className="p-2 text-center">
                      <Badge variant={
                        adj.pattern === 'Balanced' ? 'outline' :
                        adj.pattern === 'Over-Predicting' ? 'secondary' :
                        'destructive'
                      }>
                        {adj.pattern}
                      </Badge>
                    </td>
                    <td className="p-2 text-right font-semibold">{adj.avg_variance_pct.toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Complete Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Complete Adjuster Performance Details</CardTitle>
          <CardDescription>Comprehensive metrics for all adjusters</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Adjuster</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">Avg Settlement</th>
                  <th className="text-right p-2">Avg Predicted</th>
                  <th className="text-right p-2">Variance %</th>
                  <th className="text-right p-2">High Var Count</th>
                  <th className="text-right p-2">High Var %</th>
                  <th className="text-right p-2">Avg Days</th>
                </tr>
              </thead>
              <tbody>
                {data.adjusterPerformance.map((adj, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{adj.adjuster_name}</td>
                    <td className="p-2 text-right">{adj.claim_count.toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(adj.avg_actual_settlement).toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(adj.avg_predicted_settlement).toLocaleString()}</td>
                    <td className="p-2 text-right">
                      <span className={Math.abs(adj.avg_variance_pct) > 10 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                        {adj.avg_variance_pct.toFixed(2)}%
                      </span>
                    </td>
                    <td className="p-2 text-right">{adj.high_variance_count}</td>
                    <td className="p-2 text-right">{adj.high_variance_pct.toFixed(1)}%</td>
                    <td className="p-2 text-right">{Math.round(adj.avg_settlement_days)}</td>
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
