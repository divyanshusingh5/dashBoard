from fastapi import APIRouter, HTTPException
import logging

from app.api.schemas import (
    RecalibrationRequest,
    RecalibrationResponse,
    WeightOptimizationRequest,
    WeightOptimizationResponse,
)
from app.services import recalibration_service
# Switch to SQLite data service for better performance
from app.services.data_service_sqlite import data_service_sqlite as data_service
from app.services.enhanced_recalibration_service import enhanced_recalibration_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/recalibrate", response_model=RecalibrationResponse)
async def recalibrate_weights(request: RecalibrationRequest):
    """
    Recalibrate model weights and return metrics
    """
    try:
        # Get claims data if not provided
        claims_data = request.claims_data
        if not claims_data:
            claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=400, detail="No claims data available")

        # Calculate predictions with new weights
        import numpy as np
        predictions = recalibration_service.calculate_prediction_with_weights(
            claims_data,
            request.weights
        )

        # Get actual values
        import pandas as pd
        df = pd.DataFrame(claims_data)
        actuals = df['ConsensusValue'].values if 'ConsensusValue' in df.columns else df['SettlementAmount'].values

        # Calculate metrics
        metrics = recalibration_service.calculate_metrics(predictions, actuals)

        return {
            "success": True,
            "metrics": metrics,
            "message": "Recalibration completed successfully"
        }

    except Exception as e:
        logger.error(f"Error in recalibration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize", response_model=WeightOptimizationResponse)
async def optimize_weights(request: WeightOptimizationRequest):
    """
    Optimize weights to minimize variance or MAE
    """
    try:
        result = recalibration_service.optimize_weights(
            claims=request.claims,
            current_weights=request.current_weights,
            method=request.optimization_method
        )

        return {
            "optimized_weights": result.get("optimized_weights", {}),
            "improvement_metrics": result.get("improvement_metrics", {}),
            "iterations": result.get("iterations", 0),
            "converged": result.get("converged", False)
        }

    except Exception as e:
        logger.error(f"Error optimizing weights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sensitivity-analysis")
async def sensitivity_analysis(
    weights: dict,
    perturbation: float = 0.1
):
    """
    Perform sensitivity analysis on weights
    """
    try:
        # Get claims data
        claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=400, detail="No claims data available")

        # Perform sensitivity analysis
        results = recalibration_service.perform_sensitivity_analysis(
            claims=claims_data,
            base_weights=weights,
            perturbation=perturbation
        )

        return {
            "success": True,
            "sensitivity_results": results
        }

    except Exception as e:
        logger.error(f"Error in sensitivity analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/default-weights")
async def get_default_weights():
    """
    Get default weight configuration
    """
    return {
        "weights": recalibration_service.default_weights
    }

@router.post("/compare-weights")
async def compare_weights(
    weights_a: dict,
    weights_b: dict
):
    """
    Compare two sets of weights
    """
    try:
        # Get claims data
        claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=400, detail="No claims data available")

        import pandas as pd
        df = pd.DataFrame(claims_data)
        actuals = df['ConsensusValue'].values if 'ConsensusValue' in df.columns else df['SettlementAmount'].values

        # Calculate predictions for both weight sets
        predictions_a = recalibration_service.calculate_prediction_with_weights(claims_data, weights_a)
        predictions_b = recalibration_service.calculate_prediction_with_weights(claims_data, weights_b)

        # Calculate metrics
        metrics_a = recalibration_service.calculate_metrics(predictions_a, actuals)
        metrics_b = recalibration_service.calculate_metrics(predictions_b, actuals)

        return {
            "weights_a_metrics": metrics_a,
            "weights_b_metrics": metrics_b,
            "comparison": {
                "mae_difference": metrics_a['mae'] - metrics_b['mae'],
                "rmse_difference": metrics_a['rmse'] - metrics_b['rmse'],
                "better_weights": "weights_a" if metrics_a['mae'] < metrics_b['mae'] else "weights_b"
            }
        }

    except Exception as e:
        logger.error(f"Error comparing weights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weights/config")
async def get_weight_configuration():
    """
    Get modular weight configuration with categories and constraints
    """
    try:
        import pandas as pd

        weight_config = {
            "categories": {
                "causation": {
                    "description": "Factors related to causation and liability",
                    "weights": {
                        "causation_probability": {"value": 0.20, "min": 0.10, "max": 0.30, "description": "Overall causation probability"},
                        "causation_tx_delay": {"value": 0.05, "min": 0.00, "max": 0.10, "description": "Treatment delay impact"},
                        "causation_tx_gaps": {"value": 0.05, "min": 0.00, "max": 0.10, "description": "Treatment gaps impact"},
                        "causation_compliance": {"value": 0.05, "min": 0.00, "max": 0.10, "description": "Patient compliance"}
                    }
                },
                "severity": {
                    "description": "Factors related to injury severity",
                    "weights": {
                        "severity_score": {"value": 0.25, "min": 0.15, "max": 0.35, "description": "Overall severity score"},
                        "severity_initial_tx": {"value": 0.05, "min": 0.00, "max": 0.10, "description": "Initial treatment severity"},
                        "severity_injections": {"value": 0.03, "min": 0.00, "max": 0.08, "description": "Injection treatments"},
                        "severity_objective_findings": {"value": 0.07, "min": 0.00, "max": 0.12, "description": "Objective medical findings"}
                    }
                },
                "venue": {
                    "description": "Venue and jurisdiction factors",
                    "weights": {
                        "venue_rating": {"value": 0.15, "min": 0.05, "max": 0.25, "description": "Venue rating impact"},
                        "ratingweight": {"value": 0.05, "min": 0.00, "max": 0.15, "description": "Rating weight modifier"}
                    }
                },
                "impact": {
                    "description": "Impact and consequences",
                    "weights": {
                        "impact": {"value": 0.10, "min": 0.05, "max": 0.20, "description": "Overall impact score"}
                    }
                }
            },
            "constraints": {
                "total_must_equal": 1.0,
                "individual_min": 0.0,
                "individual_max": 0.5
            },
            "presets": {
                "conservative": "Lower weights for subjective factors",
                "balanced": "Equal distribution across categories",
                "liberal": "Higher weights for severity and impact"
            }
        }

        return weight_config

    except Exception as e:
        logger.error(f"Error getting weight configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weights/data")
async def get_weights_csv_data():
    """
    Serve the weights.csv data from backend
    Returns the weight factors with their base, min, max values and categories
    """
    try:
        import pandas as pd
        import os

        # Path to weights.csv in backend data folder
        weights_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "weights.csv")

        if not os.path.exists(weights_path):
            raise HTTPException(status_code=404, detail="weights.csv file not found")

        # Read the CSV file
        df = pd.read_csv(weights_path)

        # Convert to list of dictionaries for JSON response
        weights_data = df.to_dict(orient='records')

        return {
            "success": True,
            "data": weights_data,
            "total_factors": len(weights_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading weights CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weights/update")
async def update_weights(updated_weights: dict):
    """
    Update and validate weight configuration
    Ensures weights sum to 1.0 and are within constraints
    """
    try:
        # Validate weights
        total = sum(updated_weights.values())

        if abs(total - 1.0) > 0.01:
            # Auto-normalize if close
            if abs(total - 1.0) <= 0.1:
                normalized_weights = {k: v / total for k, v in updated_weights.items()}
                return {
                    "status": "normalized",
                    "message": f"Weights were normalized from {total:.4f} to 1.0",
                    "weights": normalized_weights,
                    "original_total": total
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Weights must sum to 1.0 (current: {total:.4f})"
                )

        # Validate individual weights
        for key, value in updated_weights.items():
            if value < 0 or value > 0.5:
                raise HTTPException(
                    status_code=400,
                    detail=f"Weight '{key}' must be between 0 and 0.5 (current: {value:.4f})"
                )

        # Calculate impact metrics with new weights
        claims_data = await data_service.get_full_claims_data()

        if claims_data:
            import pandas as pd
            df = pd.DataFrame(claims_data)
            actuals = df['ConsensusValue'].values if 'ConsensusValue' in df.columns else df['DOLLARAMOUNTHIGH'].values

            predictions = recalibration_service.calculate_prediction_with_weights(claims_data, updated_weights)
            metrics = recalibration_service.calculate_metrics(predictions, actuals)
        else:
            metrics = {}

        return {
            "status": "success",
            "message": "Weights updated successfully",
            "weights": updated_weights,
            "total": sum(updated_weights.values()),
            "metrics": metrics
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating weights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENHANCED RECALIBRATION ENDPOINTS - Statistical Analysis & Recommendations
# ============================================================================

@router.post("/analyze-statistics")
async def analyze_weight_statistics(
    weight_column: str,
    target_column: str = "variance_pct"
):
    """
    Analyze statistical properties of a weight factor
    Returns mean, median, mode, correlation, and distribution insights
    """
    try:
        claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=404, detail="No claims data available")

        result = enhanced_recalibration_service.analyze_weight_statistics(
            claims_data=claims_data,
            weight_column=weight_column,
            target_column=target_column
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing weight statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-similar-cases")
async def find_similar_cases(
    target_claim: dict,
    similarity_factors: list = None,
    max_results: int = 10
):
    """
    Find similar cases based on key factors
    Used for weight recommendation based on historical patterns
    """
    try:
        claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=404, detail="No claims data available")

        result = enhanced_recalibration_service.find_similar_cases(
            claims_data=claims_data,
            target_claim=target_claim,
            similarity_factors=similarity_factors,
            max_results=max_results
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-performance")
async def analyze_recent_performance(months: int = 12):
    """
    Analyze performance over recent period (one-year rolling window)
    Determines if weight updates are needed
    """
    try:
        claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=404, detail="No claims data available")

        result = enhanced_recalibration_service.analyze_recent_performance(
            claims_data=claims_data,
            months=months
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing recent performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-optimal-weights")
async def suggest_optimal_weights(
    current_weights: dict,
    keep_factors_constant: list = None,
    focus_recent_data: bool = True,
    months: int = 12
):
    """
    Suggest optimal weights based on statistical analysis
    Can keep certain factors constant while optimizing others
    Includes mean, median, mode analysis and correlation-based recommendations
    """
    try:
        claims_data = await data_service.get_full_claims_data()

        if not claims_data:
            raise HTTPException(status_code=404, detail="No claims data available")

        result = enhanced_recalibration_service.suggest_optimal_weights(
            claims_data=claims_data,
            current_weights=current_weights,
            keep_factors_constant=keep_factors_constant,
            focus_recent_data=focus_recent_data,
            months=months
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting optimal weights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
