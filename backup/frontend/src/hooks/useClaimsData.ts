import { useState, useMemo, useEffect } from 'react';
import { ClaimData, FilterState } from '@/types/claims';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function useClaimsData() {
  const [allData, setAllData] = useState<ClaimData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        console.log('Loading claims data from API...');
        const response = await axios.get(`${API_BASE_URL}/claims/claims/full`, {
          timeout: 60000
        });

        const raw: any[] = Array.isArray(response.data) ? response.data : (response.data?.claims || []);

        // Normalize records to use actual schema fields and derive what we need for filters
        const normalized = raw.map((d) => {
          const closeDate: string = d.CLAIMCLOSEDDATE || '';
          const year = closeDate ? String(closeDate).slice(0, 4) : '';

          const injuryGroupCode = d.PRIMARY_INJURYGROUP_CODE || '';
          const venueRating = d.VENUERATING || '';
          const impact = d.IOL ?? null;

          // Use actual severity score from backend, or calculate if missing
          const severityScore = d.SEVERITY_SCORE ?? (
            Number.isFinite(d.DOLLARAMOUNTHIGH) && d.DOLLARAMOUNTHIGH !== null
              ? (d.DOLLARAMOUNTHIGH <= 10000 ? 3 : d.DOLLARAMOUNTHIGH <= 25000 ? 5 : d.DOLLARAMOUNTHIGH <= 50000 ? 7 : d.DOLLARAMOUNTHIGH <= 100000 ? 9 : 10)
              : 5
          );

          const cautionLevel = d.CAUTION_LEVEL || (severityScore <= 4 ? 'Low' : severityScore <= 8 ? 'Medium' : 'High');

          return {
            ...d,
            __year: year,
            __injuryGroupCode: injuryGroupCode,
            __venueRating: venueRating,
            __impact: impact,
            __severityScore: severityScore,
            __cautionLevel: cautionLevel,
          };
        });

        console.log(`✅ Loaded ${normalized.length} claims from API`);
        setAllData(normalized as any);
        setIsLoading(false);
      } catch (err: any) {
        console.error('Failed to load claims data from API:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to load data from API');
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  const [filters, setFilters] = useState<FilterState>({
    injuryGroupCode: 'all',
    county: 'all',
    severityScore: 'all',
    cautionLevel: 'all',
    venueRating: 'all',
    impact: 'all',
    year: 'all'
  });

  const filteredData = useMemo(() => {
    return allData.filter((claim: any) => {
      if (filters.injuryGroupCode !== 'all' && claim.__injuryGroupCode !== filters.injuryGroupCode) return false;
      if (filters.county !== 'all' && claim.COUNTYNAME !== filters.county) return false;
      if (filters.venueRating !== 'all' && claim.__venueRating !== filters.venueRating) return false;
      if (filters.impact !== 'all' && String(claim.__impact) !== String(filters.impact)) return false;
      if (filters.year !== 'all' && claim.__year !== filters.year) return false;

      if (filters.severityScore !== 'all') {
        if (filters.severityScore === 'low' && claim.__severityScore > 4) return false;
        if (filters.severityScore === 'medium' && (claim.__severityScore <= 4 || claim.__severityScore > 8)) return false;
        if (filters.severityScore === 'high' && claim.__severityScore <= 8) return false;
      }

      if (filters.cautionLevel !== 'all') {
        if (filters.cautionLevel === 'Low' && claim.__cautionLevel !== 'Low') return false;
        if (filters.cautionLevel === 'Medium' && claim.__cautionLevel !== 'Medium') return false;
        if (filters.cautionLevel === 'High' && claim.__cautionLevel !== 'High') return false;
      }

      return true;
    });
  }, [allData, filters]);

  const updateFilter = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const counties = useMemo(() => {
    const uniqueCounties = [...new Set((allData as any[]).map(d => d.COUNTYNAME).filter(Boolean))];
    return uniqueCounties.sort();
  }, [allData]);

  const years = useMemo(() => {
    const uniqueYears = [...new Set((allData as any[]).map(d => d.__year).filter(Boolean))];
    return uniqueYears.sort();
  }, [allData]);

  const injuryGroups = useMemo(() => {
    const uniqueGroups = [...new Set((allData as any[]).map(d => d.__injuryGroupCode).filter(Boolean))];
    return uniqueGroups.sort();
  }, [allData]);

  const venueRatings = useMemo(() => {
    const uniqueRatings = [...new Set((allData as any[]).map(d => d.__venueRating).filter(Boolean))];
    return uniqueRatings.sort();
  }, [allData]);

  const impactLevels = useMemo(() => {
    const uniqueImpacts = [...new Set((allData as any[]).map(d => d.__impact).filter((v) => v !== null && v !== undefined))] as number[];
    return uniqueImpacts.sort((a, b) => Number(a) - Number(b));
  }, [allData]);

  return { filteredData, filters, updateFilter, counties, years, injuryGroups, venueRatings, impactLevels, isLoading, error };
}
