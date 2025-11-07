import { useState, useEffect } from 'react';
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

      // Try backend API first
      try {
        const backendResponse = await fetch('http://localhost:8000/api/recalibration/weights/data');
        if (backendResponse.ok) {
          const result = await backendResponse.json();
          if (result?.success && Array.isArray(result?.data)) {
            setWeights(result.data);
            setLoading(false);
            return;
          } else if (Array.isArray(result)) {
            setWeights(result);
            setLoading(false);
            return;
          }
        }
      } catch (apiErr) {
        console.warn('Backend API not available, trying direct CSV load...');
      }

      // Fallback: Load weights_summary.csv directly from public folder
      // NOTE: Copy backend/data/weights_summary.csv to frontend/public/weights_summary.csv
      const csvResponse = await fetch('/weights_summary.csv');
      if (!csvResponse.ok) {
        throw new Error('Failed to load weights summary CSV');
      }

      const csvText = await csvResponse.text();
      const rows = csvText.split('\n');
      const headers = rows[0].split(',');

      const weightsData = rows.slice(1).filter(row => row.trim()).map(row => {
        const values = row.split(',');
        const obj: any = {};
        headers.forEach((header, i) => {
          obj[header.trim()] = values[i]?.trim();
        });
        return {
          factor_name: obj.factor_name,
          base_weight: parseFloat(obj.base_weight),
          min_weight: parseFloat(obj.min_weight),
          max_weight: parseFloat(obj.max_weight),
          category: obj.category,
          description: obj.description
        };
      });

      setWeights(weightsData);
      setLoading(false);
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
