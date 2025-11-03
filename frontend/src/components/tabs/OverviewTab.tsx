import { ClaimData } from "@/types/claims";
import { KPICard } from "../dashboard/KPICard";
import { VarianceTrendChart } from "../charts/VarianceTrendChart";
import { SeverityChart } from "../charts/SeverityChart";
import { ActualVsPredictedChart } from "../charts/ActualVsPredictedChart";
import { DeviationAnalysisTable } from "../charts/DeviationAnalysisTable";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Calendar, AlertTriangle, ArrowUpCircle, ArrowDownCircle, DollarSign } from "lucide-react";

interface OverviewTabProps {
  data: ClaimData[];
}

export function OverviewTab({ data }: OverviewTabProps) {
  // Calculate KPIs
  const currentYear = '2025';
  const lastYear = '2024';
  
  const currentData = data.filter(d => d.claim_date.startsWith(currentYear));
  const lyData = data.filter(d => d.claim_date.startsWith(lastYear));
  
  const totalClaims = currentData.length;
  const lyTotalClaims = lyData.length;
  const claimsChange = ((totalClaims - lyTotalClaims) / lyTotalClaims) * 100;
  
  const avgSettlement = currentData.length > 0 
    ? currentData.reduce((sum, d) => sum + d.DOLLARAMOUNTHIGH, 0) / currentData.length 
    : 0;
  const lyAvgSettlement = lyData.length > 0 
    ? lyData.reduce((sum, d) => sum + d.DOLLARAMOUNTHIGH, 0) / lyData.length 
    : 0;
  const settlementChange = ((avgSettlement - lyAvgSettlement) / lyAvgSettlement) * 100;
  
  const avgDays = currentData.length > 0 
    ? currentData.reduce((sum, d) => sum + d.SETTLEMENT_DAYS, 0) / currentData.length 
    : 0;
  const lyAvgDays = lyData.length > 0 
    ? lyData.reduce((sum, d) => sum + d.SETTLEMENT_DAYS, 0) / lyData.length 
    : 0;
  const daysChange = ((avgDays - lyAvgDays) / lyAvgDays) * 100;
  
  const highVarianceClaims = currentData.filter(d => Math.abs(d.variance_pct) > 25).length;
  const highVariancePct = currentData.length > 0 ? (highVarianceClaims / currentData.length) * 100 : 0;
  const lyHighVariance = lyData.filter(d => Math.abs(d.variance_pct) > 25).length;
  const lyHighVariancePct = lyData.length > 0 ? (lyHighVariance / lyData.length) * 100 : 0;
  const varianceChange = ((highVariancePct - lyHighVariancePct) / lyHighVariancePct) * 100;
  
  // Overprediction and Underprediction KPIs
  const overpredictedClaims = currentData.filter(d => d.predicted_pain_suffering > d.DOLLARAMOUNTHIGH).length;
  const overpredictionPct = currentData.length > 0 ? (overpredictedClaims / currentData.length) * 100 : 0;
  const lyOverpredicted = lyData.filter(d => d.predicted_pain_suffering > d.DOLLARAMOUNTHIGH).length;
  const lyOverpredictionPct = lyData.length > 0 ? (lyOverpredicted / lyData.length) * 100 : 0;
  const overpredictionChange = lyOverpredictionPct > 0 ? ((overpredictionPct - lyOverpredictionPct) / lyOverpredictionPct) * 100 : 0;
  
  const underpredictedClaims = currentData.filter(d => d.predicted_pain_suffering < d.DOLLARAMOUNTHIGH).length;
  const underpredictionPct = currentData.length > 0 ? (underpredictedClaims / currentData.length) * 100 : 0;
  const lyUnderpredicted = lyData.filter(d => d.predicted_pain_suffering < d.DOLLARAMOUNTHIGH).length;
  const lyUnderpredictionPct = lyData.length > 0 ? (lyUnderpredicted / lyData.length) * 100 : 0;
  const underpredictionChange = lyUnderpredictionPct > 0 ? ((underpredictionPct - lyUnderpredictionPct) / lyUnderpredictionPct) * 100 : 0;
  
  // Priority claims table
  const priorityClaims = data
    .filter(d => Math.abs(d.variance_pct) > 25)
    .sort((a, b) => Math.abs(b.variance_pct) - Math.abs(a.variance_pct))
    .slice(0, 8);

  return (
    <div className="space-y-6">
      {/* Deviation Analysis */}
      <DeviationAnalysisTable data={data} />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <KPICard
          title="Total Claims"
          value={totalClaims}
          change={{
            value: claimsChange,
            isPositive: claimsChange > 0,
          }}
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <KPICard
          title="Avg Settlement"
          value={`$${Math.round(avgSettlement).toLocaleString()}`}
          change={{
            value: settlementChange,
            isPositive: settlementChange > 0,
          }}
          icon={<DollarSign className="h-5 w-5" />}
        />
        <KPICard
          title="Avg Days to Settle"
          value={Math.round(avgDays)}
          change={{
            value: daysChange,
            isPositive: daysChange < 0,
            isInverted: true,
          }}
          icon={<Calendar className="h-5 w-5" />}
        />
        <KPICard
          title="High Variance Claims"
          value={`${highVariancePct.toFixed(1)}%`}
          change={{
            value: varianceChange,
            isPositive: varianceChange < 0,
            isInverted: true,
          }}
          icon={<AlertTriangle className="h-5 w-5" />}
        />
        <KPICard
          title="Overprediction Rate"
          value={`${overpredictionPct.toFixed(1)}%`}
          change={{
            value: overpredictionChange,
            isPositive: overpredictionChange < 0,
            isInverted: true,
          }}
          icon={<ArrowUpCircle className="h-5 w-5" />}
        />
        <KPICard
          title="Underprediction Rate"
          value={`${underpredictionPct.toFixed(1)}%`}
          change={{
            value: underpredictionChange,
            isPositive: underpredictionChange < 0,
            isInverted: true,
          }}
          icon={<ArrowDownCircle className="h-5 w-5" />}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-lg font-semibold mb-4">Model Variance Trend</h3>
          <div className="h-[250px]">
            <VarianceTrendChart data={data} />
          </div>
        </div>
        
        <div className="bg-card rounded-xl p-6 border border-border shadow-md">
          <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
          <div className="h-[250px]">
            <SeverityChart data={data} />
          </div>
        </div>
        
        <div className="bg-card rounded-xl p-6 border border-border shadow-md lg:col-span-2 xl:col-span-1">
          <h3 className="text-lg font-semibold mb-4">Actual vs Predicted</h3>
          <div className="h-[250px]">
            <ActualVsPredictedChart data={data} />
          </div>
        </div>
      </div>

      {/* Priority Table */}
      <div className="bg-card rounded-xl p-6 border border-border shadow-md">
        <h3 className="text-lg font-semibold mb-4">Recalibration Priority Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold">Claim ID</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">County</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Injury Group</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Severity</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Actual ($)</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Predicted ($)</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Variance</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Priority</th>
              </tr>
            </thead>
            <tbody>
              {priorityClaims.map((claim, idx) => (
                <tr key={claim.claim_id} className="border-b border-border hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-primary">{claim.claim_id}</td>
                  <td className="px-4 py-3 text-sm">{claim.COUNTYNAME}</td>
                  <td className="px-4 py-3 text-sm">{claim.INJURY_GROUP_CODE}</td>
                  <td className="px-4 py-3 text-sm">{claim.SEVERITY_SCORE.toFixed(1)}</td>
                  <td className="px-4 py-3 text-sm">${claim.DOLLARAMOUNTHIGH.toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm">${Math.round(claim.predicted_pain_suffering).toLocaleString()}</td>
                  <td className={`px-4 py-3 text-sm font-semibold ${claim.variance_pct > 0 ? 'text-destructive' : 'text-success'}`}>
                    {claim.variance_pct > 0 ? '+' : ''}{claim.variance_pct.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <Badge variant={Math.abs(claim.variance_pct) > 40 ? 'destructive' : 'default'}>
                      {Math.abs(claim.variance_pct) > 40 ? 'Critical' : 'High'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
