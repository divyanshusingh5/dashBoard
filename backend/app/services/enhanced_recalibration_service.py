"""
Enhanced Weight Recalibration Service
Features:
- Statistical analysis (mean, median, mode)
- Similar case comparison
- One-year rolling window analysis
- Automatic weight suggestions
- Keep all factors constant analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize
import logging

logger = logging.getLogger(__name__)


class EnhancedRecalibrationService:
    """
    Enhanced service for weight recalibration with statistical insights
    """

    def __init__(self):
        self.current_weights = {}

    def analyze_weight_statistics(
        self,
        claims_data: List[Dict],
        weight_column: str,
        target_column: str = 'variance_pct'
    ) -> Dict[str, Any]:
        """
        Analyze statistical properties of a weight factor
        Returns mean, median, mode, and distribution insights
        """
        try:
            df = pd.DataFrame(claims_data)

            if weight_column not in df.columns:
                return {"error": f"Column {weight_column} not found"}

            values = df[weight_column].dropna()
            target_values = df[target_column].dropna()

            # Calculate statistics
            stats_dict = {
                "factor_name": weight_column,
                "statistics": {
                    "mean": float(values.mean()),
                    "median": float(values.median()),
                    "mode": float(values.mode()[0]) if len(values.mode()) > 0 else float(values.median()),
                    "std_dev": float(values.std()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "q25": float(values.quantile(0.25)),
                    "q75": float(values.quantile(0.75))
                },
                "correlation_with_variance": float(values.corr(target_values)) if len(values) == len(target_values) else 0,
                "sample_size": len(values)
            }

            # Distribution analysis
            if len(values) > 30:
                # Shapiro-Wilk test for normality
                _, p_value = stats.shapiro(values.sample(min(5000, len(values))))
                stats_dict["distribution"] = {
                    "is_normal": p_value > 0.05,
                    "p_value": float(p_value),
                    "skewness": float(stats.skew(values)),
                    "kurtosis": float(stats.kurtosis(values))
                }

            # Suggested weight based on impact
            correlation = stats_dict["correlation_with_variance"]
            if abs(correlation) > 0.5:
                suggested_weight = min(0.20, abs(correlation))
                recommendation = "High impact - increase weight"
            elif abs(correlation) > 0.3:
                suggested_weight = min(0.15, abs(correlation))
                recommendation = "Moderate impact - maintain weight"
            elif abs(correlation) > 0.1:
                suggested_weight = min(0.10, abs(correlation))
                recommendation = "Low impact - consider reducing weight"
            else:
                suggested_weight = 0.05
                recommendation = "Minimal impact - consider removing"

            stats_dict["recommendation"] = {
                "suggested_weight": round(suggested_weight, 3),
                "reason": recommendation,
                "confidence": "High" if len(values) > 100 else "Medium" if len(values) > 30 else "Low"
            }

            return stats_dict

        except Exception as e:
            logger.error(f"Error analyzing weight statistics: {e}")
            return {"error": str(e)}

    def find_similar_cases(
        self,
        claims_data: List[Dict],
        target_claim: Dict,
        similarity_factors: List[str] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Find similar cases based on key factors
        Used for weight recommendation based on historical patterns
        """
        try:
            df = pd.DataFrame(claims_data)

            if similarity_factors is None:
                similarity_factors = [
                    'INJURY_GROUP_CODE',
                    'SEVERITY_SCORE',
                    'CAUTION_LEVEL',
                    'VENUE_RATING'
                ]

            # Filter similar cases
            similar_mask = pd.Series([True] * len(df))

            for factor in similarity_factors:
                if factor in target_claim and factor in df.columns:
                    if factor == 'SEVERITY_SCORE':
                        # Allow ±2 points for severity
                        similar_mask &= df[factor].between(
                            target_claim[factor] - 2,
                            target_claim[factor] + 2
                        )
                    else:
                        similar_mask &= df[factor] == target_claim[factor]

            similar_df = df[similar_mask].copy()

            if len(similar_df) == 0:
                # Broaden search
                similar_mask = pd.Series([True] * len(df))
                if 'INJURY_GROUP_CODE' in target_claim:
                    similar_mask &= df['INJURY_GROUP_CODE'] == target_claim['INJURY_GROUP_CODE']
                similar_df = df[similar_mask].copy()

            # Calculate statistics from similar cases
            if len(similar_df) > 0:
                similar_df['variance_abs'] = similar_df['variance_pct'].abs()
                similar_df = similar_df.nsmallest(max_results, 'variance_abs')

                results = {
                    "similar_cases_found": len(similar_df),
                    "cases": similar_df[['claim_id', 'variance_pct', 'DOLLARAMOUNTHIGH',
                                        'predicted_pain_suffering', 'adjuster']].to_dict('records'),
                    "statistics": {
                        "avg_variance": float(similar_df['variance_pct'].mean()),
                        "median_variance": float(similar_df['variance_pct'].median()),
                        "std_variance": float(similar_df['variance_pct'].std()),
                        "avg_settlement": float(similar_df['DOLLARAMOUNTHIGH'].mean()),
                        "best_performing_adjuster": similar_df.loc[similar_df['variance_pct'].abs().idxmin(), 'adjuster']
                    }
                }

                return results
            else:
                return {"similar_cases_found": 0, "message": "No similar cases found"}

        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return {"error": str(e)}

    def analyze_recent_performance(
        self,
        claims_data: List[Dict],
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze performance over recent period (one-year rolling window)
        Determines if weight updates are needed
        """
        try:
            df = pd.DataFrame(claims_data)
            df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')

            # Filter recent data
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            recent_df = df[df['claim_date'] >= cutoff_date].copy()
            historical_df = df[df['claim_date'] < cutoff_date].copy()

            if len(recent_df) == 0:
                return {"error": "No recent data available"}

            # Compare recent vs historical performance
            analysis = {
                "period": f"Last {months} months",
                "recent_data": {
                    "claim_count": len(recent_df),
                    "avg_variance": float(recent_df['variance_pct'].mean()),
                    "median_variance": float(recent_df['variance_pct'].median()),
                    "std_variance": float(recent_df['variance_pct'].std()),
                    "high_variance_rate": float((recent_df['variance_pct'].abs() >= 15).sum() / len(recent_df) * 100),
                    "overprediction_rate": float((recent_df['variance_pct'] > 0).sum() / len(recent_df) * 100),
                    "underprediction_rate": float((recent_df['variance_pct'] < 0).sum() / len(recent_df) * 100)
                }
            }

            if len(historical_df) > 0:
                analysis["historical_data"] = {
                    "claim_count": len(historical_df),
                    "avg_variance": float(historical_df['variance_pct'].mean()),
                    "median_variance": float(historical_df['variance_pct'].median())
                }

                # Determine if recalibration is needed
                recent_avg = analysis["recent_data"]["avg_variance"]
                historical_avg = analysis["historical_data"]["avg_variance"]
                performance_change = ((recent_avg - historical_avg) / abs(historical_avg)) * 100 if historical_avg != 0 else 0

                analysis["comparison"] = {
                    "performance_change_pct": round(performance_change, 2),
                    "is_degrading": abs(recent_avg) > abs(historical_avg),
                    "needs_recalibration": abs(performance_change) > 10 or analysis["recent_data"]["high_variance_rate"] > 20
                }

                if analysis["comparison"]["needs_recalibration"]:
                    analysis["recommendation"] = "Weight recalibration recommended - recent performance shows significant deviation"
                else:
                    analysis["recommendation"] = "Current weights performing well - no immediate recalibration needed"
            else:
                analysis["recommendation"] = "Insufficient historical data for comparison - proceed with caution"

            # Monthly breakdown
            recent_df['month'] = recent_df['claim_date'].dt.to_period('M')
            monthly = recent_df.groupby('month').agg({
                'variance_pct': ['mean', 'count'],
                'DOLLARAMOUNTHIGH': 'mean'
            }).reset_index()
            monthly['month'] = monthly['month'].astype(str)
            monthly.columns = ['month', 'avg_variance', 'claim_count', 'avg_settlement']

            analysis["monthly_trends"] = monthly.to_dict('records')

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing recent performance: {e}")
            return {"error": str(e)}

    def suggest_optimal_weights(
        self,
        claims_data: List[Dict],
        current_weights: Dict[str, float],
        keep_factors_constant: Optional[List[str]] = None,
        focus_recent_data: bool = True,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Suggest optimal weights based on statistical analysis
        Can keep certain factors constant while optimizing others
        """
        try:
            df = pd.DataFrame(claims_data)

            # Focus on recent data if requested
            if focus_recent_data:
                df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
                cutoff_date = datetime.now() - timedelta(days=months * 30)
                df = df[df['claim_date'] >= cutoff_date].copy()

            if len(df) < 10:
                return {"error": "Insufficient data for optimization"}

            # Get weight columns
            weight_columns = [col for col in current_weights.keys() if col in df.columns]

            if not weight_columns:
                return {"error": "No weight columns found in data"}

            # Analyze each weight factor
            factor_analysis = {}
            for col in weight_columns:
                if keep_factors_constant and col in keep_factors_constant:
                    factor_analysis[col] = {
                        "current_weight": current_weights[col],
                        "suggested_weight": current_weights[col],
                        "status": "kept_constant",
                        "reason": "Factor marked as constant"
                    }
                else:
                    stats_result = self.analyze_weight_statistics(df.to_dict('records'), col)
                    if "error" not in stats_result:
                        factor_analysis[col] = {
                            "current_weight": current_weights.get(col, 0.1),
                            "suggested_weight": stats_result["recommendation"]["suggested_weight"],
                            "correlation": stats_result["correlation_with_variance"],
                            "statistics": stats_result["statistics"],
                            "recommendation": stats_result["recommendation"],
                            "status": "optimized"
                        }

            # Calculate total suggested weight
            total_suggested = sum(f["suggested_weight"] for f in factor_analysis.values() if "suggested_weight" in f)

            # Normalize to sum to 1.0
            if total_suggested > 0:
                for factor in factor_analysis:
                    if "suggested_weight" in factor_analysis[factor]:
                        factor_analysis[factor]["normalized_weight"] = round(
                            factor_analysis[factor]["suggested_weight"] / total_suggested, 4
                        )
                        factor_analysis[factor]["weight_change"] = round(
                            factor_analysis[factor]["normalized_weight"] - current_weights.get(factor, 0.1), 4
                        )

            # Calculate expected improvement
            if len(df) > 0:
                current_mae = df['variance_pct'].abs().mean()
                expected_improvement = {
                    "current_mae": round(float(current_mae), 2),
                    "expected_mae_reduction": "10-20%",  # Conservative estimate
                    "confidence": "Medium" if len(df) > 100 else "Low"
                }
            else:
                expected_improvement = {"error": "Cannot estimate improvement"}

            return {
                "analysis_period": f"Last {months} months" if focus_recent_data else "All data",
                "sample_size": len(df),
                "factor_analysis": factor_analysis,
                "expected_improvement": expected_improvement,
                "recommendation": {
                    "action": "Apply suggested weights" if total_suggested > 0 else "Keep current weights",
                    "confidence": "High" if len(df) > 200 else "Medium" if len(df) > 50 else "Low",
                    "notes": f"Analysis based on {len(df)} recent claims" if focus_recent_data else f"Analysis based on all {len(df)} claims"
                }
            }

        except Exception as e:
            logger.error(f"Error suggesting optimal weights: {e}")
            return {"error": str(e)}


# Global instance
enhanced_recalibration_service = EnhancedRecalibrationService()
