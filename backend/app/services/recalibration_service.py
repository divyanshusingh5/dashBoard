import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import logging
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

class RecalibrationService:
    """Service for weight recalibration and optimization"""

    def __init__(self):
        self.default_weights = {
            "injury_severity": 0.25,
            "medical_costs": 0.20,
            "lost_wages": 0.15,
            "jurisdiction": 0.15,
            "liability": 0.10,
            "age": 0.08,
            "treatment_duration": 0.07
        }

    def calculate_prediction_with_weights(
        self,
        claims: List[Dict[str, Any]],
        weights: Dict[str, float]
    ) -> np.ndarray:
        """Calculate predictions using given weights"""
        try:
            df = pd.DataFrame(claims)

            # Create factor matrix (normalized)
            factors = []
            for weight_key in weights.keys():
                if weight_key in df.columns:
                    factor_values = df[weight_key].fillna(0).values
                    # Normalize
                    if factor_values.max() > 0:
                        factor_values = factor_values / factor_values.max()
                    factors.append(factor_values)
                else:
                    # Generate synthetic factor if not present
                    factors.append(np.random.rand(len(df)))

            factor_matrix = np.column_stack(factors)
            weight_vector = np.array(list(weights.values()))

            predictions = np.dot(factor_matrix, weight_vector)

            # Scale to reasonable settlement amounts
            if 'ConsensusValue' in df.columns:
                avg_consensus = df['ConsensusValue'].mean()
                predictions = predictions * avg_consensus / predictions.mean()

            return predictions

        except Exception as e:
            logger.error(f"Error calculating predictions: {str(e)}")
            return np.array([])

    def calculate_metrics(
        self,
        predictions: np.ndarray,
        actuals: np.ndarray
    ) -> Dict[str, float]:
        """Calculate performance metrics"""
        try:
            mae = np.mean(np.abs(predictions - actuals))
            rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
            mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100

            variance = predictions - actuals
            total_variance = np.sum(variance)
            avg_variance = np.mean(variance)

            r_squared = 1 - (np.sum((actuals - predictions) ** 2) /
                           np.sum((actuals - np.mean(actuals)) ** 2))

            return {
                "mae": float(mae),
                "rmse": float(rmse),
                "mape": float(mape),
                "r_squared": float(r_squared),
                "total_variance": float(total_variance),
                "avg_variance": float(avg_variance)
            }
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}

    def optimize_weights(
        self,
        claims: List[Dict[str, Any]],
        current_weights: Dict[str, float],
        method: str = "variance_minimization"
    ) -> Dict[str, Any]:
        """Optimize weights to minimize variance"""
        try:
            df = pd.DataFrame(claims)
            actuals = df['ConsensusValue'].values if 'ConsensusValue' in df.columns else df['SettlementAmount'].values

            weight_keys = list(current_weights.keys())
            initial_weights = np.array(list(current_weights.values()))

            def objective_function(weights_array):
                """Objective function to minimize"""
                weights_dict = dict(zip(weight_keys, weights_array))
                predictions = self.calculate_prediction_with_weights(claims, weights_dict)

                if method == "variance_minimization":
                    return np.sum((predictions - actuals) ** 2)
                elif method == "mae_minimization":
                    return np.mean(np.abs(predictions - actuals))
                else:
                    return np.sum((predictions - actuals) ** 2)

            # Constraints: weights sum to 1 and are non-negative
            constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
            bounds = [(0.0, 1.0) for _ in weight_keys]

            result = minimize(
                objective_function,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )

            optimized_weights = dict(zip(weight_keys, result.x))

            # Calculate metrics for optimized weights
            optimized_predictions = self.calculate_prediction_with_weights(claims, optimized_weights)
            optimized_metrics = self.calculate_metrics(optimized_predictions, actuals)

            # Calculate metrics for current weights
            current_predictions = self.calculate_prediction_with_weights(claims, current_weights)
            current_metrics = self.calculate_metrics(current_predictions, actuals)

            improvement = {
                "mae_improvement": (current_metrics['mae'] - optimized_metrics['mae']) / current_metrics['mae'] * 100,
                "rmse_improvement": (current_metrics['rmse'] - optimized_metrics['rmse']) / current_metrics['rmse'] * 100,
                "variance_reduction": (abs(current_metrics['avg_variance']) - abs(optimized_metrics['avg_variance'])) / abs(current_metrics['avg_variance']) * 100
            }

            return {
                "optimized_weights": optimized_weights,
                "improvement_metrics": improvement,
                "current_metrics": current_metrics,
                "optimized_metrics": optimized_metrics,
                "iterations": result.nit,
                "converged": result.success
            }

        except Exception as e:
            logger.error(f"Error optimizing weights: {str(e)}")
            return {
                "optimized_weights": current_weights,
                "improvement_metrics": {},
                "iterations": 0,
                "converged": False,
                "error": str(e)
            }

    def perform_sensitivity_analysis(
        self,
        claims: List[Dict[str, Any]],
        base_weights: Dict[str, float],
        perturbation: float = 0.1
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on weights"""
        try:
            df = pd.DataFrame(claims)
            actuals = df['ConsensusValue'].values if 'ConsensusValue' in df.columns else df['SettlementAmount'].values

            base_predictions = self.calculate_prediction_with_weights(claims, base_weights)
            base_metrics = self.calculate_metrics(base_predictions, actuals)

            sensitivity_results = {}

            for weight_key in base_weights.keys():
                # Increase weight
                increased_weights = base_weights.copy()
                increased_weights[weight_key] = min(1.0, base_weights[weight_key] * (1 + perturbation))
                # Renormalize
                total = sum(increased_weights.values())
                increased_weights = {k: v/total for k, v in increased_weights.items()}

                increased_predictions = self.calculate_prediction_with_weights(claims, increased_weights)
                increased_metrics = self.calculate_metrics(increased_predictions, actuals)

                # Decrease weight
                decreased_weights = base_weights.copy()
                decreased_weights[weight_key] = max(0.0, base_weights[weight_key] * (1 - perturbation))
                # Renormalize
                total = sum(decreased_weights.values())
                decreased_weights = {k: v/total for k, v in decreased_weights.items()}

                decreased_predictions = self.calculate_prediction_with_weights(claims, decreased_weights)
                decreased_metrics = self.calculate_metrics(decreased_predictions, actuals)

                sensitivity_results[weight_key] = {
                    "base_mae": base_metrics['mae'],
                    "increased_mae": increased_metrics['mae'],
                    "decreased_mae": decreased_metrics['mae'],
                    "sensitivity_score": abs(increased_metrics['mae'] - decreased_metrics['mae']) / base_metrics['mae']
                }

            return sensitivity_results

        except Exception as e:
            logger.error(f"Error in sensitivity analysis: {str(e)}")
            return {}

# Singleton instance
recalibration_service = RecalibrationService()
