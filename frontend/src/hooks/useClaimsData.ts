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

        console.log(`✅ Loaded ${response.data.length} claims from API`);
        setAllData(response.data);
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
    return allData.filter(claim => {
      if (filters.injuryGroupCode !== 'all' && claim.INJURY_GROUP_CODE !== filters.injuryGroupCode) return false;
      if (filters.county !== 'all' && claim.COUNTYNAME !== filters.county) return false;
      if (filters.venueRating !== 'all' && claim.VENUE_RATING !== filters.venueRating) return false;
      if (filters.impact !== 'all' && claim.IMPACT !== parseInt(filters.impact)) return false;
      if (filters.year !== 'all' && !claim.claim_date.startsWith(filters.year)) return false;
      
      if (filters.severityScore !== 'all') {
        if (filters.severityScore === 'low' && claim.SEVERITY_SCORE > 4) return false;
        if (filters.severityScore === 'medium' && (claim.SEVERITY_SCORE <= 4 || claim.SEVERITY_SCORE > 8)) return false;
        if (filters.severityScore === 'high' && claim.SEVERITY_SCORE <= 8) return false;
      }
      
      if (filters.cautionLevel !== 'all') {
        if (filters.cautionLevel === 'Low' && claim.CAUTION_LEVEL !== 'Low') return false;
        if (filters.cautionLevel === 'Medium' && claim.CAUTION_LEVEL !== 'Medium') return false;
        if (filters.cautionLevel === 'High' && claim.CAUTION_LEVEL !== 'High') return false;
      }
      
      return true;
    });
  }, [allData, filters]);

  const updateFilter = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const counties = useMemo(() => {
    const uniqueCounties = [...new Set(allData.map(d => d.COUNTYNAME))];
    return uniqueCounties.sort();
  }, [allData]);

  const years = useMemo(() => {
    const uniqueYears = [...new Set(allData.map(d => d.claim_date.substring(0, 4)))];
    return uniqueYears.sort();
  }, [allData]);

  const injuryGroups = useMemo(() => {
    const uniqueGroups = [...new Set(allData.map(d => d.INJURY_GROUP_CODE))];
    return uniqueGroups.sort();
  }, [allData]);

  const venueRatings = useMemo(() => {
    const uniqueRatings = [...new Set(allData.map(d => d.VENUE_RATING))];
    return uniqueRatings.sort();
  }, [allData]);

  const impactLevels = useMemo(() => {
    const uniqueImpacts = [...new Set(allData.map(d => d.IMPACT))];
    return uniqueImpacts.sort((a, b) => a - b);
  }, [allData]);

  return { filteredData, filters, updateFilter, counties, years, injuryGroups, venueRatings, impactLevels, isLoading, error };
}
