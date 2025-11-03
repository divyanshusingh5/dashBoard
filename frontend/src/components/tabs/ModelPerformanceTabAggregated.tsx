import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AggregatedData } from "@/hooks/useAggregatedClaimsData";
import { useMemo } from "react";
import { Activity, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";

interface ModelPerformanceTabAggregatedProps {
  data: AggregatedData | null;
}

export function ModelPerformanceTabAggregated({ data }: ModelPerformanceTabAggregatedProps) {
  if (!data) {
    return (
      <div className="p-8 text-center">
        <p className="text-muted-foreground">Loading model performance...</p>
      </div>
    );
  }

  // Calculate overall model performance metrics
  const overallMetrics = useMemo(() => {
    const totalClaims = data.yearSeverity.reduce((sum, s) => sum + s.claim_count, 0);
    const totalActual = data.yearSeverity.reduce((sum, s) => sum + s.total_actual_settlement, 0);
    const totalPredicted = data.yearSeverity.reduce((sum, s) => sum + s.total_predicted_settlement, 0);

    // Calculate weighted average variance (MAPE - Mean Absolute Percentage Error)
    const weightedVariance = data.yearSeverity.reduce((sum, s) =>
      sum + (Math.abs(s.avg_variance_pct) * s.claim_count), 0);
    const mape = totalClaims > 0 ? weightedVariance / totalClaims : 0;

    // Calculate RMSE approximation (Root Mean Square Error)
    const squaredErrors = data.yearSeverity.reduce((sum, s) => {
      const avgError = (s.total_actual_settlement - s.total_predicted_settlement) / s.claim_count;
      return sum + (avgError * avgError * s.claim_count);
    }, 0);
    const rmse = totalClaims > 0 ? Math.sqrt(squaredErrors / totalClaims) : 0;

    // Accuracy within thresholds
    const totalHighVariance = data.yearSeverity.reduce((sum, s) => sum + s.high_variance_count, 0);
    const accurateWithin10Pct = totalClaims - totalHighVariance; // Assuming high variance is >10%
    const accuracyRate = totalClaims > 0 ? (accurateWithin10Pct / totalClaims) * 100 : 0;

    // Over/under prediction
    const totalOver = data.yearSeverity.reduce((sum, s) => sum + s.overprediction_count, 0);
    const totalUnder = data.yearSeverity.reduce((sum, s) => sum + s.underprediction_count, 0);

    // Bias (average signed error)
    const totalSignedError = totalActual - totalPredicted;
    const avgBias = totalClaims > 0 ? totalSignedError / totalClaims : 0;
    const biasPct = totalPredicted > 0 ? (avgBias / (totalPredicted / totalClaims)) * 100 : 0;

    return {
      totalClaims,
      mape,
      rmse,
      accuracyRate,
      totalOver,
      totalUnder,
      overpredictionRate: totalClaims > 0 ? (totalOver / totalClaims) * 100 : 0,
      underpredictionRate: totalClaims > 0 ? (totalUnder / totalClaims) * 100 : 0,
      avgBias,
      biasPct,
      avgActual: totalClaims > 0 ? totalActual / totalClaims : 0,
      avgPredicted: totalClaims > 0 ? totalPredicted / totalClaims : 0,
    };
  }, [data]);

  // Performance by severity
  const performanceBySeverity = useMemo(() => {
    const severityOrder = { 'Low': 1, 'Medium': 2, 'High': 3 };

    return data.yearSeverity.reduce((acc, item) => {
      const existing = acc.find(s => s.severity === item.severity_category);
      if (existing) {
        existing.claimCount += item.claim_count;
        existing.totalActual += item.total_actual_settlement;
        existing.totalPredicted += item.total_predicted_settlement;
        existing.highVarianceCount += item.high_variance_count;
        existing.overpredictionCount += item.overprediction_count;
        existing.underpredictionCount += item.underprediction_count;
        existing.weightedVariance += Math.abs(item.avg_variance_pct) * item.claim_count;
      } else {
        acc.push({
          severity: item.severity_category,
          claimCount: item.claim_count,
          totalActual: item.total_actual_settlement,
          totalPredicted: item.total_predicted_settlement,
          highVarianceCount: item.high_variance_count,
          overpredictionCount: item.overprediction_count,
          underpredictionCount: item.underprediction_count,
          weightedVariance: Math.abs(item.avg_variance_pct) * item.claim_count,
        });
      }
      return acc;
    }, [] as any[]).map(s => ({
      ...s,
      avgActual: s.claimCount > 0 ? s.totalActual / s.claimCount : 0,
      avgPredicted: s.claimCount > 0 ? s.totalPredicted / s.claimCount : 0,
      mape: s.claimCount > 0 ? s.weightedVariance / s.claimCount : 0,
      accuracyRate: s.claimCount > 0 ? ((s.claimCount - s.highVarianceCount) / s.claimCount) * 100 : 0,
      overpredictionRate: s.claimCount > 0 ? (s.overpredictionCount / s.claimCount) * 100 : 0,
      underpredictionRate: s.claimCount > 0 ? (s.underpredictionCount / s.claimCount) * 100 : 0,
    })).sort((a, b) =>
      (severityOrder[a.severity as keyof typeof severityOrder] || 99) -
      (severityOrder[b.severity as keyof typeof severityOrder] || 99)
    );
  }, [data]);

  // Performance by year
  const performanceByYear = useMemo(() => {
    return data.yearSeverity.reduce((acc, item) => {
      const existing = acc.find(y => y.year === item.year);
      if (existing) {
        existing.claimCount += item.claim_count;
        existing.totalActual += item.total_actual_settlement;
        existing.totalPredicted += item.total_predicted_settlement;
        existing.highVarianceCount += item.high_variance_count;
        existing.weightedVariance += Math.abs(item.avg_variance_pct) * item.claim_count;
      } else {
        acc.push({
          year: item.year,
          claimCount: item.claim_count,
          totalActual: item.total_actual_settlement,
          totalPredicted: item.total_predicted_settlement,
          highVarianceCount: item.high_variance_count,
          weightedVariance: Math.abs(item.avg_variance_pct) * item.claim_count,
        });
      }
      return acc;
    }, [] as any[]).map(y => ({
      ...y,
      avgActual: y.claimCount > 0 ? y.totalActual / y.claimCount : 0,
      avgPredicted: y.claimCount > 0 ? y.totalPredicted / y.claimCount : 0,
      mape: y.claimCount > 0 ? y.weightedVariance / y.claimCount : 0,
      accuracyRate: y.claimCount > 0 ? ((y.claimCount - y.highVarianceCount) / y.claimCount) * 100 : 0,
    })).sort((a, b) => b.year - a.year);
  }, [data]);

  // Performance by injury group
  const performanceByInjuryGroup = useMemo(() => {
    return data.injuryGroup.reduce((acc, item) => {
      const existing = acc.find(i => i.injuryGroup === item.injury_group);
      if (existing) {
        existing.claimCount += item.claim_count;
        existing.totalSettlement += item.total_settlement;
        existing.totalPredicted += item.avg_predicted * item.claim_count;
        existing.weightedVariance += Math.abs(item.avg_variance_pct) * item.claim_count;
      } else {
        acc.push({
          injuryGroup: item.injury_group,
          claimCount: item.claim_count,
          totalSettlement: item.total_settlement,
          totalPredicted: item.avg_predicted * item.claim_count,
          weightedVariance: Math.abs(item.avg_variance_pct) * item.claim_count,
        });
      }
      return acc;
    }, [] as any[]).map(i => ({
      ...i,
      avgActual: i.claimCount > 0 ? i.totalSettlement / i.claimCount : 0,
      avgPredicted: i.claimCount > 0 ? i.totalPredicted / i.claimCount : 0,
      mape: i.claimCount > 0 ? i.weightedVariance / i.claimCount : 0,
    })).sort((a, b) => b.mape - a.mape);
  }, [data]);

  // Performance by venue
  const performanceByVenue = useMemo(() => {
    return data.venueAnalysis.reduce((acc, item) => {
      const existing = acc.find(v => v.venueRating === item.venue_rating);
      if (existing) {
        existing.claimCount += item.claim_count;
        existing.totalSettlement += item.avg_settlement * item.claim_count;
        existing.totalPredicted += item.avg_predicted * item.claim_count;
        existing.weightedVariance += Math.abs(item.avg_variance_pct) * item.claim_count;
      } else {
        acc.push({
          venueRating: item.venue_rating,
          claimCount: item.claim_count,
          totalSettlement: item.avg_settlement * item.claim_count,
          totalPredicted: item.avg_predicted * item.claim_count,
          weightedVariance: Math.abs(item.avg_variance_pct) * item.claim_count,
        });
      }
      return acc;
    }, [] as any[]).map(v => ({
      ...v,
      avgActual: v.claimCount > 0 ? v.totalSettlement / v.claimCount : 0,
      avgPredicted: v.claimCount > 0 ? v.totalPredicted / v.claimCount : 0,
      mape: v.claimCount > 0 ? v.weightedVariance / v.claimCount : 0,
    })).sort((a, b) => b.mape - a.mape);
  }, [data]);

  // Model health assessment
  const modelHealth = useMemo(() => {
    const issues: string[] = [];
    const strengths: string[] = [];

    if (overallMetrics.mape > 15) {
      issues.push(`High MAPE (${overallMetrics.mape.toFixed(2)}%) - Model needs retraining`);
    } else if (overallMetrics.mape < 5) {
      strengths.push(`Excellent MAPE (${overallMetrics.mape.toFixed(2)}%)`);
    }

    if (overallMetrics.accuracyRate < 80) {
      issues.push(`Low accuracy rate (${overallMetrics.accuracyRate.toFixed(1)}%) - Less than 80% within 10% variance`);
    } else if (overallMetrics.accuracyRate > 90) {
      strengths.push(`High accuracy rate (${overallMetrics.accuracyRate.toFixed(1)}%)`);
    }

    if (Math.abs(overallMetrics.biasPct) > 5) {
      const biasDirection = overallMetrics.biasPct > 0 ? 'under-predicting' : 'over-predicting';
      issues.push(`Systematic bias detected (${Math.abs(overallMetrics.biasPct).toFixed(2)}% ${biasDirection})`);
    } else {
      strengths.push('Well-calibrated predictions (minimal bias)');
    }

    // Check for performance degradation over time
    if (performanceByYear.length >= 2) {
      const latestYear = performanceByYear[0];
      const previousYear = performanceByYear[1];
      if (latestYear.mape > previousYear.mape * 1.2) {
        issues.push('Performance degrading over time - urgent retraining needed');
      }
    }

    // Check for specific category issues
    const worstInjuryGroup = performanceByInjuryGroup[0];
    if (worstInjuryGroup && worstInjuryGroup.mape > 20) {
      issues.push(`Poor performance on ${worstInjuryGroup.injuryGroup} injuries (${worstInjuryGroup.mape.toFixed(1)}% MAPE)`);
    }

    return { issues, strengths };
  }, [overallMetrics, performanceByYear, performanceByInjuryGroup]);

  return (
    <div className="space-y-6 p-6">
      {/* Model Health Alert */}
      {modelHealth.issues.length > 0 ? (
        <Alert className="border-red-500 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertTitle className="text-red-900">Model Performance Issues Detected</AlertTitle>
          <AlertDescription className="text-red-800">
            <ul className="list-disc list-inside space-y-1 mt-2">
              {modelHealth.issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-green-500 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-900">Model Performing Well</AlertTitle>
          <AlertDescription className="text-green-800">
            <ul className="list-disc list-inside space-y-1 mt-2">
              {modelHealth.strengths.map((strength, idx) => (
                <li key={idx}>{strength}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Overall Performance Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">MAPE</CardTitle>
            <CardDescription className="text-xs">Mean Absolute % Error</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallMetrics.mape.toFixed(2)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              {overallMetrics.mape < 10 ? 'Excellent' : overallMetrics.mape < 15 ? 'Good' : 'Needs Improvement'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">RMSE</CardTitle>
            <CardDescription className="text-xs">Root Mean Square Error</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${(overallMetrics.rmse / 1000).toFixed(1)}K</div>
            <p className="text-xs text-muted-foreground mt-1">
              Avg error magnitude
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Accuracy Rate</CardTitle>
            <CardDescription className="text-xs">Within 10% variance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallMetrics.accuracyRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              {overallMetrics.accuracyRate > 85 ? 'Strong' : overallMetrics.accuracyRate > 75 ? 'Moderate' : 'Weak'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Model Bias</CardTitle>
            <CardDescription className="text-xs">Systematic error direction</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallMetrics.biasPct.toFixed(2)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              {overallMetrics.biasPct > 5 ? 'Under-predicting' : overallMetrics.biasPct < -5 ? 'Over-predicting' : 'Balanced'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Prediction Distribution */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Over-Predictions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{overallMetrics.totalOver.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {overallMetrics.overpredictionRate.toFixed(1)}% of total claims
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Under-Predictions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{overallMetrics.totalUnder.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {overallMetrics.underpredictionRate.toFixed(1)}% of total claims
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Prediction</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${Math.round(overallMetrics.avgPredicted).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Actual: ${Math.round(overallMetrics.avgActual).toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance by Severity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Model Performance by Severity Level
          </CardTitle>
          <CardDescription>How well the model predicts different severity categories</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Severity</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">MAPE</th>
                  <th className="text-right p-2">Accuracy Rate</th>
                  <th className="text-right p-2">Avg Actual</th>
                  <th className="text-right p-2">Avg Predicted</th>
                  <th className="text-right p-2">Over %</th>
                  <th className="text-right p-2">Under %</th>
                </tr>
              </thead>
              <tbody>
                {performanceBySeverity.map((sev, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2">
                      <Badge variant={
                        sev.severity === 'Low' ? 'outline' :
                        sev.severity === 'Medium' ? 'secondary' :
                        'destructive'
                      }>
                        {sev.severity}
                      </Badge>
                    </td>
                    <td className="p-2 text-right font-semibold">{sev.claimCount.toLocaleString()}</td>
                    <td className="p-2 text-right">
                      <span className={sev.mape > 15 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                        {sev.mape.toFixed(2)}%
                      </span>
                    </td>
                    <td className="p-2 text-right">{sev.accuracyRate.toFixed(1)}%</td>
                    <td className="p-2 text-right">${Math.round(sev.avgActual).toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(sev.avgPredicted).toLocaleString()}</td>
                    <td className="p-2 text-right text-blue-600">{sev.overpredictionRate.toFixed(0)}%</td>
                    <td className="p-2 text-right text-orange-600">{sev.underpredictionRate.toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Performance by Year */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Model Performance Over Time
          </CardTitle>
          <CardDescription>Tracking model accuracy trends by year</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Year</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">MAPE</th>
                  <th className="text-right p-2">Accuracy Rate</th>
                  <th className="text-right p-2">Avg Actual</th>
                  <th className="text-right p-2">Avg Predicted</th>
                  <th className="text-center p-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {performanceByYear.map((year, idx) => {
                  const isLatest = idx === 0;
                  const isPrevious = idx === 1;
                  let trend = '';
                  if (isLatest && isPrevious) {
                    const prevMape = performanceByYear[1].mape;
                    if (year.mape < prevMape * 0.9) trend = 'Improving';
                    else if (year.mape > prevMape * 1.1) trend = 'Degrading';
                    else trend = 'Stable';
                  }

                  return (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="p-2 font-semibold">{year.year}</td>
                      <td className="p-2 text-right">{year.claimCount.toLocaleString()}</td>
                      <td className="p-2 text-right">
                        <span className={year.mape > 15 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                          {year.mape.toFixed(2)}%
                        </span>
                      </td>
                      <td className="p-2 text-right">{year.accuracyRate.toFixed(1)}%</td>
                      <td className="p-2 text-right">${Math.round(year.avgActual).toLocaleString()}</td>
                      <td className="p-2 text-right">${Math.round(year.avgPredicted).toLocaleString()}</td>
                      <td className="p-2 text-center">
                        {isLatest && trend && (
                          <Badge variant={
                            trend === 'Improving' ? 'default' :
                            trend === 'Degrading' ? 'destructive' :
                            'outline'
                          }>
                            {trend}
                          </Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Performance by Injury Group */}
      <Card className="border-orange-200">
        <CardHeader>
          <CardTitle className="text-orange-700">Worst Performing Injury Groups</CardTitle>
          <CardDescription>Injury types with highest prediction errors - prioritize for model improvement</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Injury Group</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">MAPE</th>
                  <th className="text-right p-2">Avg Actual</th>
                  <th className="text-right p-2">Avg Predicted</th>
                  <th className="text-center p-2">Priority</th>
                </tr>
              </thead>
              <tbody>
                {performanceByInjuryGroup.slice(0, 10).map((injury, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{injury.injuryGroup}</td>
                    <td className="p-2 text-right">{injury.claimCount.toLocaleString()}</td>
                    <td className="p-2 text-right">
                      <span className="text-red-600 font-semibold">{injury.mape.toFixed(2)}%</span>
                    </td>
                    <td className="p-2 text-right">${Math.round(injury.avgActual).toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(injury.avgPredicted).toLocaleString()}</td>
                    <td className="p-2 text-center">
                      <Badge variant={idx < 3 ? 'destructive' : 'outline'}>
                        {idx < 3 ? 'High' : 'Medium'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Performance by Venue Rating */}
      <Card>
        <CardHeader>
          <CardTitle>Model Performance by Venue Rating</CardTitle>
          <CardDescription>Prediction accuracy across different venue types</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Venue Rating</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">MAPE</th>
                  <th className="text-right p-2">Avg Actual</th>
                  <th className="text-right p-2">Avg Predicted</th>
                </tr>
              </thead>
              <tbody>
                {performanceByVenue.map((venue, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{venue.venueRating}</td>
                    <td className="p-2 text-right">{venue.claimCount.toLocaleString()}</td>
                    <td className="p-2 text-right">
                      <span className={venue.mape > 15 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                        {venue.mape.toFixed(2)}%
                      </span>
                    </td>
                    <td className="p-2 text-right">${Math.round(venue.avgActual).toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(venue.avgPredicted).toLocaleString()}</td>
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
