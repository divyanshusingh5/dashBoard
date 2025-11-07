import { apiClient } from './client';
import { ClaimData } from './claimsAPI';

export interface RecalibrationRequest {
  weights: Record<string, number>;
  claims_data?: ClaimData[];
}

export interface RecalibrationResponse {
  success: boolean;
  metrics: {
    mae: number;
    rmse: number;
    mape: number;
    r_squared: number;
    total_variance: number;
    avg_variance: number;
  };
  optimized_weights?: Record<string, number>;
  message: string;
}

export interface WeightOptimizationRequest {
  claims: ClaimData[];
  current_weights: Record<string, number>;
  optimization_method?: string;
}

export interface WeightOptimizationResponse {
  optimized_weights: Record<string, number>;
  improvement_metrics: {
    mae_improvement: number;
    rmse_improvement: number;
    variance_reduction: number;
  };
  iterations: number;
  converged: boolean;
}

export interface SensitivityAnalysisResponse {
  success: boolean;
  sensitivity_results: Record<string, {
    base_mae: number;
    increased_mae: number;
    decreased_mae: number;
    sensitivity_score: number;
  }>;
}

export const recalibrationAPI = {
  // Recalibrate weights
  recalibrateWeights: async (request: RecalibrationRequest): Promise<RecalibrationResponse> => {
    return apiClient.post('/recalibration/recalibrate', request);
  },

  // Optimize weights
  optimizeWeights: async (request: WeightOptimizationRequest): Promise<WeightOptimizationResponse> => {
    return apiClient.post('/recalibration/optimize', request);
  },

  // Perform sensitivity analysis
  sensitivityAnalysis: async (
    weights: Record<string, number>,
    perturbation: number = 0.1
  ): Promise<SensitivityAnalysisResponse> => {
    return apiClient.post('/recalibration/sensitivity-analysis', {
      weights,
      perturbation,
    });
  },

  // Get default weights
  getDefaultWeights: async (): Promise<{ weights: Record<string, number> }> => {
    return apiClient.get('/recalibration/default-weights');
  },

  // Compare two sets of weights
  compareWeights: async (
    weights_a: Record<string, number>,
    weights_b: Record<string, number>
  ) => {
    return apiClient.post('/recalibration/compare-weights', {
      weights_a,
      weights_b,
    });
  },

  // Get weight configuration
  getWeightConfiguration: async () => {
    return apiClient.get('/recalibration/weights/config');
  },

  // Update weights with validation
  updateWeights: async (updated_weights: Record<string, number>) => {
    return apiClient.post('/recalibration/weights/update', updated_weights);
  },
};

export default recalibrationAPI;
