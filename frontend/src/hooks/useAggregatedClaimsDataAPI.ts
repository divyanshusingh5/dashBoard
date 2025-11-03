/**
 * Hook to load aggregated data from backend API
 * Replaces CSV loading with API calls for better performance and scalability
 */

import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Type definitions (same as before)
export interface YearSeveritySummary {
  year: number;
  severity_category: string;
  claim_count: number;
  total_actual_settlement: number;
  total_predicted_settlement: number;
  avg_actual_settlement: number;
  avg_predicted_settlement: number;
  avg_variance_pct: number;
  avg_settlement_days: number;
  overprediction_count: number;
  underprediction_count: number;
  high_variance_count: number;
}

export interface CountyYearSummary {
  county: string;
  state: string;
  year: number;
  venue_rating: string;
  claim_count: number;
  total_settlement: number;
  avg_settlement: number;
  avg_variance_pct: number;
  high_variance_count: number;
  high_variance_pct: number;
  overprediction_count: number;
  underprediction_count: number;
}

export interface InjuryGroupSummary {
  injury_group: string;
  body_region: string;
  severity_category: string;
  claim_count: number;
  avg_settlement: number;
  avg_predicted: number;
  avg_variance_pct: number;
  avg_settlement_days: number;
  total_settlement: number;
}

export interface AdjusterPerformanceSummary {
  adjuster_name: string;
  claim_count: number;
  avg_actual_settlement: number;
  avg_predicted_settlement: number;
  avg_variance_pct: number;
  high_variance_count: number;
  high_variance_pct: number;
  overprediction_count: number;
  underprediction_count: number;
  avg_settlement_days: number;
}

export interface VenueAnalysisSummary {
  venue_rating: string;
  state: string;
  county: string;
  claim_count: number;
  avg_settlement: number;
  avg_predicted: number;
  avg_variance_pct: number;
  avg_venue_rating_point: number;
  high_variance_pct: number;
}

export interface VarianceDriverAnalysis {
  factor_name: string;
  factor_value: string;
  claim_count: number;
  avg_variance_pct: number;
  contribution_score: number;
  correlation_strength: string;
}

export interface AggregatedData {
  yearSeverity: YearSeveritySummary[];
  countyYear: CountyYearSummary[];
  injuryGroup: InjuryGroupSummary[];
  adjusterPerformance: AdjusterPerformanceSummary[];
  venueAnalysis: VenueAnalysisSummary[];
  varianceDrivers: VarianceDriverAnalysis[];
}

export function useAggregatedClaimsDataAPI() {
  const [data, setData] = useState<AggregatedData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        console.log('Loading aggregated data from API...');

        const response = await axios.get(`${API_BASE_URL}/aggregation/aggregated`, {
          timeout: 60000 // 60 second timeout for aggregation
        });
        const apiData = response.data;

        console.log('✅ API data loaded:', {
          yearSeverity: apiData.yearSeverity?.length,
          countyYear: apiData.countyYear?.length,
          injuryGroup: apiData.injuryGroup?.length,
          adjusterPerformance: apiData.adjusterPerformance?.length,
          venueAnalysis: apiData.venueAnalysis?.length,
          varianceDrivers: apiData.varianceDrivers?.length,
        });

        setData(apiData);
        setIsLoading(false);
      } catch (err: any) {
        console.error('Failed to load aggregated data:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to load data from API');
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  // Calculate KPIs from aggregated data
  const kpis = useMemo(() => {
    if (!data || !data.yearSeverity.length) {
      return {
        totalClaims: 0,
        avgSettlement: 0,
        avgDays: 0,
        highVariancePct: 0,
        overpredictionRate: 0,
        underpredictionRate: 0,
      };
    }

    const totalClaims = data.yearSeverity.reduce((sum, s) => sum + s.claim_count, 0);
    const totalActual = data.yearSeverity.reduce((sum, s) => sum + s.total_actual_settlement, 0);
    const totalDays = data.yearSeverity.reduce((sum, s) => sum + (s.avg_settlement_days * s.claim_count), 0);

    const avgSettlement = totalClaims > 0 ? totalActual / totalClaims : 0;
    const avgDays = totalClaims > 0 ? totalDays / totalClaims : 0;

    const totalOverprediction = data.yearSeverity.reduce((sum, s) => sum + s.overprediction_count, 0);
    const totalUnderprediction = data.yearSeverity.reduce((sum, s) => sum + s.underprediction_count, 0);
    const totalHighVariance = data.yearSeverity.reduce((sum, s) => sum + s.high_variance_count, 0);

    return {
      totalClaims,
      avgSettlement: Math.round(avgSettlement),
      avgDays: Math.round(avgDays),
      highVariancePct: totalClaims > 0 ? (totalHighVariance / totalClaims) * 100 : 0,
      overpredictionRate: totalClaims > 0 ? (totalOverprediction / totalClaims) * 100 : 0,
      underpredictionRate: totalClaims > 0 ? (totalUnderprediction / totalClaims) * 100 : 0,
    };
  }, [data]);

  // Extract unique values for filters
  const filterOptions = useMemo(() => {
    if (!data) {
      return {
        counties: [],
        years: [],
        injuryGroups: [],
        venueRatings: [],
        severityCategories: [],
        adjusters: [],
      };
    }

    return {
      counties: [...new Set(data.countyYear.map(d => d.county))].sort(),
      years: [...new Set(data.yearSeverity.map(d => d.year))].sort(),
      injuryGroups: [...new Set(data.injuryGroup.map(d => d.injury_group))].sort(),
      venueRatings: [...new Set(data.venueAnalysis.map(d => d.venue_rating))].sort(),
      severityCategories: [...new Set(data.yearSeverity.map(d => d.severity_category))].sort(),
      adjusters: [...new Set(data.adjusterPerformance.map(d => d.adjuster_name))].sort(),
    };
  }, [data]);

  return {
    data,
    kpis,
    filterOptions,
    isLoading,
    error,
  };
}
