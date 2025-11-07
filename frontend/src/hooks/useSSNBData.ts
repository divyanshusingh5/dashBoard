import { useState, useEffect } from 'react';
import { SSNBData } from '@/types/claims';

interface UseSSNBDataReturn {
  data: SSNBData[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSSNBData(limit?: number): UseSSNBDataReturn {
  const [data, setData] = useState<SSNBData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSSNB = async () => {
    try {
      setLoading(true);
      setError(null);

      const url = limit
        ? `http://localhost:8000/api/v1/claims/ssnb?limit=${limit}`
        : 'http://localhost:8000/api/v1/claims/ssnb';

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result.ssnb_data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching SSNB data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch SSNB data');
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSSNB();
  }, [limit]);

  return { data, loading, error, refetch: fetchSSNB };
}
