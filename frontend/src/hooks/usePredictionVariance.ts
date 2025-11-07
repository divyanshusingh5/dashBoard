import { useState, useEffect } from 'react';
import { PredictionVarianceResponse } from '@/types/claims';

interface UsePredictionVarianceReturn {
  data: PredictionVarianceResponse | null;
  loading: boolean;
  error: string | null;
  refetch: (threshold?: number, limit?: number) => Promise<void>;
}

export function usePredictionVariance(
  varianceThreshold: number = 50.0,
  limit: number = 1000
): UsePredictionVarianceReturn {
  const [data, setData] = useState<PredictionVarianceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVarianceData = async (threshold?: number, lim?: number) => {
    try {
      setLoading(true);
      setError(null);

      const thresholdValue = threshold ?? varianceThreshold;
      const limitValue = lim ?? limit;

      const url = `http://localhost:8000/api/v1/claims/prediction-variance?variance_threshold=${thresholdValue}&limit=${limitValue}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      console.error('Error fetching prediction variance data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch prediction variance data');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVarianceData();
  }, [varianceThreshold, limit]);

  return { data, loading, error, refetch: fetchVarianceData };
}
