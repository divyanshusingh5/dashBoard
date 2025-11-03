import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { WeightConfig } from '../types/claims';

export function useWeightsData() {
  const [weights, setWeights] = useState<WeightConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWeights();
  }, []);

  const loadWeights = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch from backend API first
      try {
        const backendResponse = await fetch('http://localhost:8000/api/recalibration/weights/data');
        if (backendResponse.ok) {
          const result = await backendResponse.json();
          if (result.success && result.data) {
            setWeights(result.data);
            setLoading(false);
            return;
          }
        }
      } catch (backendError) {
        console.warn('Backend API not available, falling back to public folder:', backendError);
      }

      // Fallback: Load from public folder (for backward compatibility)
      const response = await fetch('/weights.csv');
      if (!response.ok) {
        throw new Error('Failed to load weights.csv from both backend and public folder');
      }

      const csvText = await response.text();

      Papa.parse<WeightConfig>(csvText, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length > 0) {
            console.error('CSV parsing errors:', results.errors);
            setError('Error parsing weights CSV file');
          } else {
            setWeights(results.data);
          }
          setLoading(false);
        },
        error: (parseError) => {
          console.error('CSV parsing error:', parseError);
          setError('Error parsing weights CSV file');
          setLoading(false);
        },
      });
    } catch (err) {
      console.error('Error loading weights:', err);
      setError(err instanceof Error ? err.message : 'Unknown error loading weights');
      setLoading(false);
    }
  };

  const reloadWeights = () => {
    loadWeights();
  };

  return { weights, loading, error, reloadWeights };
}
