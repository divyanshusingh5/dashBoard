import { useState, useEffect } from 'react';
import { FactorCombinationResponse } from '@/types/claims';

interface UseFactorCombinationsReturn {
  data: FactorCombinationResponse | null;
  loading: boolean;
  error: string | null;
  refetch: (threshold?: number) => Promise<void>;
}

export function useFactorCombinations(
  varianceThreshold: number = 50.0
): UseFactorCombinationsReturn {
  const [data, setData] = useState<FactorCombinationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCombinations = async (threshold?: number) => {
    try {
      setLoading(true);
      setError(null);

      const thresholdValue = threshold ?? varianceThreshold;

      const url = `http://localhost:8000/api/v1/claims/factor-combinations?variance_threshold=${thresholdValue}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      console.error('Error fetching factor combinations:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch factor combinations');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCombinations();
  }, [varianceThreshold]);

  return { data, loading, error, refetch: fetchCombinations };
}
