import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AggregatedData } from "@/hooks/useAggregatedClaimsData";
import { useMemo, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface InjuryAnalysisTabAggregatedProps {
  data: AggregatedData | null;
}

export function InjuryAnalysisTabAggregated({ data }: InjuryAnalysisTabAggregatedProps) {
  const [selectedInjuryGroup, setSelectedInjuryGroup] = useState<string>("all");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");

  if (!data) {
    return (
      <div className="p-8 text-center">
        <p className="text-muted-foreground">Loading injury analysis...</p>
      </div>
    );
  }

  // Get unique injury groups and severities for filters
  const injuryGroups = useMemo(() => {
    return [...new Set(data.injuryGroup.map(i => i.injury_group))].sort();
  }, [data]);

  const severityLevels = useMemo(() => {
    return [...new Set(data.injuryGroup.map(i => i.severity_category))].sort();
  }, [data]);

  // Filter data based on selections
  const filteredData = useMemo(() => {
    return data.injuryGroup.filter(injury => {
      const matchesGroup = selectedInjuryGroup === "all" || injury.injury_group === selectedInjuryGroup;
      const matchesSeverity = selectedSeverity === "all" || injury.severity_category === selectedSeverity;
      return matchesGroup && matchesSeverity;
    });
  }, [data, selectedInjuryGroup, selectedSeverity]);

  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    if (filteredData.length === 0) {
      return {
        totalClaims: 0,
        avgSettlement: 0,
        avgVariance: 0,
        avgSettlementDays: 0,
        totalSettlement: 0,
      };
    }

    const totalClaims = filteredData.reduce((sum, i) => sum + i.claim_count, 0);
    const totalSettlement = filteredData.reduce((sum, i) => sum + i.total_settlement, 0);
    const weightedVariance = filteredData.reduce((sum, i) => sum + (i.avg_variance_pct * i.claim_count), 0);
    const weightedDays = filteredData.reduce((sum, i) => sum + (i.avg_settlement_days * i.claim_count), 0);

    return {
      totalClaims,
      avgSettlement: totalClaims > 0 ? totalSettlement / totalClaims : 0,
      avgVariance: totalClaims > 0 ? weightedVariance / totalClaims : 0,
      avgSettlementDays: totalClaims > 0 ? weightedDays / totalClaims : 0,
      totalSettlement,
    };
  }, [filteredData]);

  // Group by injury type
  const byInjuryType = useMemo(() => {
    const groups = new Map<string, typeof filteredData>();
    filteredData.forEach(injury => {
      if (!groups.has(injury.injury_group)) {
        groups.set(injury.injury_group, []);
      }
      groups.get(injury.injury_group)!.push(injury);
    });

    return Array.from(groups.entries()).map(([injuryType, injuries]) => {
      const totalClaims = injuries.reduce((sum, i) => sum + i.claim_count, 0);
      const totalSettlement = injuries.reduce((sum, i) => sum + i.total_settlement, 0);
      const avgVariance = injuries.reduce((sum, i) => sum + (i.avg_variance_pct * i.claim_count), 0) / totalClaims;

      return {
        injuryType,
        claimCount: totalClaims,
        avgSettlement: totalSettlement / totalClaims,
        avgVariance,
        injuries,
      };
    }).sort((a, b) => b.claimCount - a.claimCount);
  }, [filteredData]);

  // Group by severity
  const bySeverity = useMemo(() => {
    const groups = new Map<string, typeof filteredData>();
    filteredData.forEach(injury => {
      if (!groups.has(injury.severity_category)) {
        groups.set(injury.severity_category, []);
      }
      groups.get(injury.severity_category)!.push(injury);
    });

    const severityOrder = { 'Low': 1, 'Medium': 2, 'High': 3 };

    return Array.from(groups.entries()).map(([severity, injuries]) => {
      const totalClaims = injuries.reduce((sum, i) => sum + i.claim_count, 0);
      const totalSettlement = injuries.reduce((sum, i) => sum + i.total_settlement, 0);
      const avgVariance = injuries.reduce((sum, i) => sum + (i.avg_variance_pct * i.claim_count), 0) / totalClaims;
      const avgDays = injuries.reduce((sum, i) => sum + (i.avg_settlement_days * i.claim_count), 0) / totalClaims;

      return {
        severity,
        claimCount: totalClaims,
        avgSettlement: totalSettlement / totalClaims,
        avgVariance,
        avgDays,
      };
    }).sort((a, b) => (severityOrder[a.severity as keyof typeof severityOrder] || 99) - (severityOrder[b.severity as keyof typeof severityOrder] || 99));
  }, [filteredData]);

  // Highest/Lowest settlement injury combinations
  const sortedBySettlement = useMemo(() => {
    return [...filteredData].sort((a, b) => b.avg_settlement - a.avg_settlement);
  }, [filteredData]);

  const highestSettlement = sortedBySettlement.slice(0, 5);
  const lowestSettlement = sortedBySettlement.slice(-5).reverse();

  // Highest/Lowest variance combinations
  const sortedByVariance = useMemo(() => {
    return [...filteredData].sort((a, b) => Math.abs(b.avg_variance_pct) - Math.abs(a.avg_variance_pct));
  }, [filteredData]);

  const highestVariance = sortedByVariance.slice(0, 5);
  const lowestVariance = sortedByVariance.slice(-5).reverse();

  return (
    <div className="space-y-6 p-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter injury analysis by type and severity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Injury Group</label>
              <Select value={selectedInjuryGroup} onValueChange={setSelectedInjuryGroup}>
                <SelectTrigger>
                  <SelectValue placeholder="Select injury group" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Injury Groups</SelectItem>
                  {injuryGroups.map(group => (
                    <SelectItem key={group} value={group}>{group}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Severity Level</label>
              <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
                <SelectTrigger>
                  <SelectValue placeholder="Select severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severities</SelectItem>
                  {severityLevels.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <div className="grid md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Claims</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryStats.totalClaims.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Settlement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${Math.round(summaryStats.avgSettlement).toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Variance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryStats.avgVariance.toFixed(2)}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Days</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(summaryStats.avgSettlementDays)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Paid</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${(summaryStats.totalSettlement / 1000000).toFixed(1)}M</div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis by Injury Type */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis by Injury Type</CardTitle>
          <CardDescription>Claims volume and settlement patterns by injury group</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Injury Type</th>
                  <th className="text-right p-2">Claim Count</th>
                  <th className="text-right p-2">Avg Settlement</th>
                  <th className="text-right p-2">Avg Variance %</th>
                  <th className="text-right p-2">% of Total</th>
                </tr>
              </thead>
              <tbody>
                {byInjuryType.map((group, idx) => {
                  const pctOfTotal = (group.claimCount / summaryStats.totalClaims) * 100;
                  return (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="p-2 font-medium">{group.injuryType}</td>
                      <td className="p-2 text-right">{group.claimCount.toLocaleString()}</td>
                      <td className="p-2 text-right">${Math.round(group.avgSettlement).toLocaleString()}</td>
                      <td className="p-2 text-right">
                        <span className={Math.abs(group.avgVariance) > 10 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                          {group.avgVariance.toFixed(2)}%
                        </span>
                      </td>
                      <td className="p-2 text-right">{pctOfTotal.toFixed(1)}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Analysis by Severity */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis by Severity Level</CardTitle>
          <CardDescription>Settlement patterns across injury severity categories</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Severity</th>
                  <th className="text-right p-2">Claim Count</th>
                  <th className="text-right p-2">Avg Settlement</th>
                  <th className="text-right p-2">Avg Variance %</th>
                  <th className="text-right p-2">Avg Days</th>
                </tr>
              </thead>
              <tbody>
                {bySeverity.map((severity, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2">
                      <Badge variant={
                        severity.severity === 'Low' ? 'outline' :
                        severity.severity === 'Medium' ? 'secondary' :
                        'destructive'
                      }>
                        {severity.severity}
                      </Badge>
                    </td>
                    <td className="p-2 text-right font-semibold">{severity.claimCount.toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(severity.avgSettlement).toLocaleString()}</td>
                    <td className="p-2 text-right">{severity.avgVariance.toFixed(2)}%</td>
                    <td className="p-2 text-right">{Math.round(severity.avgDays)} days</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Highest vs Lowest Settlement Combinations */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-700">Highest Settlement Combinations</CardTitle>
            <CardDescription>Injury types with highest average settlements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {highestSettlement.map((injury, idx) => (
                <div key={idx} className="p-3 bg-red-50 rounded border border-red-200">
                  <div className="flex justify-between items-start mb-1">
                    <div className="font-semibold text-sm">{injury.injury_group}</div>
                    <div className="text-red-700 font-bold">${Math.round(injury.avg_settlement).toLocaleString()}</div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {injury.severity_category} • {injury.claim_count} claims • {injury.avg_variance_pct.toFixed(1)}% variance
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-200">
          <CardHeader>
            <CardTitle className="text-green-700">Lowest Settlement Combinations</CardTitle>
            <CardDescription>Injury types with lowest average settlements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {lowestSettlement.map((injury, idx) => (
                <div key={idx} className="p-3 bg-green-50 rounded border border-green-200">
                  <div className="flex justify-between items-start mb-1">
                    <div className="font-semibold text-sm">{injury.injury_group}</div>
                    <div className="text-green-700 font-bold">${Math.round(injury.avg_settlement).toLocaleString()}</div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {injury.severity_category} • {injury.claim_count} claims • {injury.avg_variance_pct.toFixed(1)}% variance
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Highest vs Lowest Variance Combinations */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="border-orange-200">
          <CardHeader>
            <CardTitle className="text-orange-700">Highest Variance Combinations</CardTitle>
            <CardDescription>Hardest to predict - model improvement needed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {highestVariance.map((injury, idx) => (
                <div key={idx} className="p-3 bg-orange-50 rounded border border-orange-200">
                  <div className="flex justify-between items-start mb-1">
                    <div className="font-semibold text-sm">{injury.injury_group} - {injury.severity_category}</div>
                    <Badge variant="destructive">{Math.abs(injury.avg_variance_pct).toFixed(1)}%</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {injury.claim_count} claims • ${Math.round(injury.avg_settlement).toLocaleString()} avg
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-700">Lowest Variance Combinations</CardTitle>
            <CardDescription>Most predictable - model performing well</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {lowestVariance.map((injury, idx) => (
                <div key={idx} className="p-3 bg-blue-50 rounded border border-blue-200">
                  <div className="flex justify-between items-start mb-1">
                    <div className="font-semibold text-sm">{injury.injury_group} - {injury.severity_category}</div>
                    <Badge className="bg-blue-600">{Math.abs(injury.avg_variance_pct).toFixed(1)}%</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {injury.claim_count} claims • ${Math.round(injury.avg_settlement).toLocaleString()} avg
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Table */}
      <Card>
        <CardHeader>
          <CardTitle>Detailed Injury Analysis</CardTitle>
          <CardDescription>Complete breakdown of all injury group and severity combinations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Injury Group</th>
                  <th className="text-left p-2">Severity</th>
                  <th className="text-left p-2">Body Region</th>
                  <th className="text-right p-2">Claims</th>
                  <th className="text-right p-2">Avg Settlement</th>
                  <th className="text-right p-2">Avg Predicted</th>
                  <th className="text-right p-2">Variance %</th>
                  <th className="text-right p-2">Avg Days</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((injury, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{injury.injury_group}</td>
                    <td className="p-2">
                      <Badge variant={
                        injury.severity_category === 'Low' ? 'outline' :
                        injury.severity_category === 'Medium' ? 'secondary' :
                        'destructive'
                      } className="text-xs">
                        {injury.severity_category}
                      </Badge>
                    </td>
                    <td className="p-2 text-muted-foreground">{injury.body_region}</td>
                    <td className="p-2 text-right">{injury.claim_count}</td>
                    <td className="p-2 text-right">${Math.round(injury.avg_settlement).toLocaleString()}</td>
                    <td className="p-2 text-right">${Math.round(injury.avg_predicted).toLocaleString()}</td>
                    <td className="p-2 text-right">
                      <span className={Math.abs(injury.avg_variance_pct) > 10 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                        {injury.avg_variance_pct.toFixed(2)}%
                      </span>
                    </td>
                    <td className="p-2 text-right">{Math.round(injury.avg_settlement_days)}</td>
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
