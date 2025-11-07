import { useState, useEffect } from 'react';
import {
  YearSeveritySummary,
  CountyYearSummary,
  InjuryTypeSummary,
  TreatmentSummary,
  loadAllAggregatedData
} from '@/utils/loadAggregatedData';

interface AggregatedData {
  yearSeverity: YearSeveritySummary[];
  countyYear: CountyYearSummary[];
  injuryType: InjuryTypeSummary[];
  treatment: TreatmentSummary[];
}

/**
 * Hook to load and manage aggregated data for performance-optimized dashboards
 *
 * @example
 * ```tsx
 * function Dashboard() {
 *   const { data, loading, error } = useAggregatedData();
 *
 *   if (loading) return <Loading />;
 *   if (error) return <Error message={error} />;
 *
 *   const totalClaims = data.yearSeverity.reduce((sum, s) => sum + s.claim_count, 0);
 *   return <KPICard title="Total Claims" value={totalClaims} />;
 * }
 * ```
 */
export function useAggregatedData() {
  const [data, setData] = useState<AggregatedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAllAggregatedData()
      .then(aggregatedData => {
        setData(aggregatedData);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Failed to load aggregated data');
        setLoading(false);
      });
  }, []);

  return { data, loading, error };
}

/**
 * Hook to calculate KPIs from aggregated data
 *
 * @example
 * ```tsx
 * function KPISection() {
 *   const kpis = useAggregatedKPIs();
 *
 *   return (
 *     <>
 *       <KPICard title="Total Claims" value={kpis.totalClaims} />
 *       <KPICard title="Avg Settlement" value={formatCurrency(kpis.avgSettlement)} />
 *       <KPICard title="High Variance %" value={`${kpis.highVariancePct}%`} />
 *     </>
 *   );
 * }
 * ```
 */
export function useAggregatedKPIs() {
  const { data, loading, error } = useAggregatedData();

  if (!data || loading) {
    return {
      totalClaims: 0,
      avgSettlement: 0,
      avgDaysToSettlement: 0,
      highVariancePct: 0,
      loading,
      error,
    };
  }

  // Calculate total claims from year-severity summary
  const totalClaims = data.yearSeverity.reduce((sum, s) => sum + s.claim_count, 0);

  // Calculate weighted average settlement
  const totalSettlement = data.yearSeverity.reduce((sum, s) => sum + s.total_settlement, 0);
  const avgSettlement = totalClaims > 0 ? totalSettlement / totalClaims : 0;

  // Calculate average days to settlement
  const totalDays = data.yearSeverity.reduce(
    (sum, s) => sum + s.avg_days * s.claim_count,
    0
  );
  const avgDaysToSettlement = totalClaims > 0 ? totalDays / totalClaims : 0;

  // Calculate high variance percentage from county-year data
  const totalHighVariance = data.countyYear.reduce(
    (sum, c) => sum + (c.claim_count * c.high_variance_pct / 100),
    0
  );
  const countyTotalClaims = data.countyYear.reduce((sum, c) => sum + c.claim_count, 0);
  const highVariancePct = countyTotalClaims > 0 ? (totalHighVariance / countyTotalClaims) * 100 : 0;

  return {
    totalClaims,
    avgSettlement: Math.round(avgSettlement),
    avgDaysToSettlement: Math.round(avgDaysToSettlement),
    highVariancePct: Math.round(highVariancePct),
    loading: false,
    error: null,
  };
}

/**
 * Hook to get year-over-year comparison from aggregated data
 *
 * @example
 * ```tsx
 * function YoYComparison() {
 *   const yoy = useYearOverYear();
 *
 *   return (
 *     <div>
 *       <p>Claims Change: {yoy.claimsChangePercent}%</p>
 *       <p>Settlement Change: {yoy.settlementChangePercent}%</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useYearOverYear() {
  const { data, loading, error } = useAggregatedData();

  if (!data || loading) {
    return {
      currentYearClaims: 0,
      previousYearClaims: 0,
      claimsChangePercent: 0,
      currentYearAvgSettlement: 0,
      previousYearAvgSettlement: 0,
      settlementChangePercent: 0,
      loading,
      error,
    };
  }

  const currentYear = new Date().getFullYear();
  const previousYear = currentYear - 1;

  // Calculate current year metrics
  const currentYearData = data.yearSeverity.filter(s => s.year === currentYear);
  const currentYearClaims = currentYearData.reduce((sum, s) => sum + s.claim_count, 0);
  const currentYearTotalSettlement = currentYearData.reduce((sum, s) => sum + s.total_settlement, 0);
  const currentYearAvgSettlement = currentYearClaims > 0
    ? currentYearTotalSettlement / currentYearClaims
    : 0;

  // Calculate previous year metrics
  const previousYearData = data.yearSeverity.filter(s => s.year === previousYear);
  const previousYearClaims = previousYearData.reduce((sum, s) => sum + s.claim_count, 0);
  const previousYearTotalSettlement = previousYearData.reduce((sum, s) => sum + s.total_settlement, 0);
  const previousYearAvgSettlement = previousYearClaims > 0
    ? previousYearTotalSettlement / previousYearClaims
    : 0;

  // Calculate percent changes
  const claimsChangePercent = previousYearClaims > 0
    ? ((currentYearClaims - previousYearClaims) / previousYearClaims) * 100
    : 0;

  const settlementChangePercent = previousYearAvgSettlement > 0
    ? ((currentYearAvgSettlement - previousYearAvgSettlement) / previousYearAvgSettlement) * 100
    : 0;

  return {
    currentYearClaims,
    previousYearClaims,
    claimsChangePercent: Math.round(claimsChangePercent),
    currentYearAvgSettlement: Math.round(currentYearAvgSettlement),
    previousYearAvgSettlement: Math.round(previousYearAvgSettlement),
    settlementChangePercent: Math.round(settlementChangePercent),
    loading: false,
    error: null,
  };
}

/**
 * Hook to get categorical field distributions for filtering/analysis
 *
 * @example
 * ```tsx
 * function CategoryFilter() {
 *   const categories = useCategoryDistribution('Vehicle_Impact');
 *
 *   return (
 *     <Select>
 *       {categories.map(cat => (
 *         <option key={cat.value}>{cat.value} ({cat.count})</option>
 *       ))}
 *     </Select>
 *   );
 * }
 * ```
 */
export function useCategoryDistribution(field: keyof AggregatedData) {
  const { data, loading, error } = useAggregatedData();

  if (!data || loading) {
    return { categories: [], loading, error };
  }

  // This is a placeholder - in a real implementation, you'd need to
  // either add this to aggregated data or load from main dataset
  // For now, return empty to demonstrate the pattern
  return {
    categories: [],
    loading: false,
    error: null,
  };
}
