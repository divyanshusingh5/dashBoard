"""
Analytics API Endpoints
Provides advanced analytics, adjuster recommendations, and deviation analysis
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
import pandas as pd
import numpy as np

# Switch to SQLite data service for better performance
from app.services.data_service_sqlite import data_service_sqlite as data_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/deviation-analysis")
async def get_deviation_analysis(
    min_variance_pct: float = Query(15.0, description="Minimum variance percentage to include"),
    limit: int = Query(100, ge=1, le=1000, description="Number of top deviations to return")
):
    """
    Analyze high deviation cases and identify patterns
    Returns cases with variance > min_variance_pct
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)

        # Filter high variance cases
        high_variance = df[df['variance_pct'].abs() >= min_variance_pct].copy()

        # Sort by absolute variance
        high_variance['abs_variance'] = high_variance['variance_pct'].abs()
        high_variance = high_variance.sort_values('abs_variance', ascending=False).head(limit)

        # Add severity category
        high_variance['severity_category'] = pd.cut(
            high_variance['variance_pct'],
            bins=[-float('inf'), -20, -10, 10, 20, float('inf')],
            labels=['Very Low', 'Low', 'Normal', 'High', 'Very High']
        )

        result = {
            "total_high_variance": len(high_variance),
            "avg_variance_pct": float(high_variance['variance_pct'].mean()),
            "median_variance_pct": float(high_variance['variance_pct'].median()),
            "cases": high_variance[[
                'claim_id', 'adjuster', 'INJURY_GROUP_CODE', 'PRIMARY_INJURY',
                'DOLLARAMOUNTHIGH', 'predicted_pain_suffering', 'variance_pct',
                'SEVERITY_SCORE', 'COUNTYNAME', 'VENUESTATE'
            ]].to_dict('records')
        }

        return result

    except Exception as e:
        logger.error(f"Error in deviation analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adjuster-performance")
async def get_adjuster_performance(
    min_cases: int = Query(5, description="Minimum cases for adjuster to be included")
):
    """
    Get performance metrics for all adjusters
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)

        # Group by adjuster
        adjuster_stats = df.groupby('adjuster').agg({
            'claim_id': 'count',
            'variance_pct': ['mean', 'std', 'median'],
            'DOLLARAMOUNTHIGH': 'mean',
            'SETTLEMENT_DAYS': 'mean',
            'SEVERITY_SCORE': 'mean'
        }).reset_index()

        adjuster_stats.columns = [
            'adjuster', 'total_cases', 'avg_variance_pct', 'std_variance',
            'median_variance', 'avg_settlement', 'avg_days', 'avg_severity'
        ]

        # Filter by minimum cases
        adjuster_stats = adjuster_stats[adjuster_stats['total_cases'] >= min_cases]

        # Calculate accuracy (inverse of absolute variance)
        adjuster_stats['accuracy_score'] = 100 - adjuster_stats['avg_variance_pct'].abs()
        adjuster_stats['consistency_score'] = 100 - (adjuster_stats['std_variance'] / adjuster_stats['avg_variance_pct'].abs() * 10).clip(0, 100)

        # Overall performance score
        adjuster_stats['overall_score'] = (
            adjuster_stats['accuracy_score'] * 0.6 +
            adjuster_stats['consistency_score'] * 0.4
        )

        # Rank adjusters
        adjuster_stats['rank'] = adjuster_stats['overall_score'].rank(ascending=False)
        adjuster_stats = adjuster_stats.sort_values('overall_score', ascending=False)

        return {
            "total_adjusters": len(adjuster_stats),
            "adjusters": adjuster_stats.to_dict('records')
        }

    except Exception as e:
        logger.error(f"Error in adjuster performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adjuster-recommendations/{claim_id}")
async def get_adjuster_recommendations(
    claim_id: str,
    top_n: int = Query(3, ge=1, le=10, description="Number of top adjusters to recommend")
):
    """
    Get top adjuster recommendations for a specific claim
    Based on similar cases and adjuster performance
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)

        # Find the claim
        claim = df[df['claim_id'] == claim_id]
        if claim.empty:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")

        claim_data = claim.iloc[0]

        # Find similar cases (same injury group and similar severity)
        similar_cases = df[
            (df['INJURY_GROUP_CODE'] == claim_data['INJURY_GROUP_CODE']) &
            (df['SEVERITY_SCORE'].between(claim_data['SEVERITY_SCORE'] - 2, claim_data['SEVERITY_SCORE'] + 2))
        ]

        if len(similar_cases) < 5:
            # If not enough similar cases, broaden the search
            similar_cases = df[df['INJURY_GROUP_CODE'] == claim_data['INJURY_GROUP_CODE']]

        # Calculate adjuster performance on similar cases
        adjuster_perf = similar_cases.groupby('adjuster').agg({
            'claim_id': 'count',
            'variance_pct': ['mean', 'std'],
            'SETTLEMENT_DAYS': 'mean'
        }).reset_index()

        adjuster_perf.columns = ['adjuster', 'cases_handled', 'avg_variance', 'std_variance', 'avg_days']

        # Filter adjusters with at least 3 cases
        adjuster_perf = adjuster_perf[adjuster_perf['cases_handled'] >= 3]

        # Calculate scores
        adjuster_perf['accuracy_rate'] = 100 - adjuster_perf['avg_variance'].abs()
        adjuster_perf['consistency_score'] = 100 - (adjuster_perf['std_variance'].fillna(0) * 5).clip(0, 100)
        adjuster_perf['overall_performance'] = (
            adjuster_perf['accuracy_rate'] * 0.7 +
            adjuster_perf['consistency_score'] * 0.3
        )

        # Sort and get top N
        top_adjusters = adjuster_perf.sort_values('overall_performance', ascending=False).head(top_n)

        # Add recommendation reasons
        recommendations = []
        for _, adj in top_adjusters.iterrows():
            reason = []
            if adj['accuracy_rate'] > 85:
                reason.append(f"High accuracy ({adj['accuracy_rate']:.1f}%)")
            if adj['consistency_score'] > 80:
                reason.append(f"Consistent performance")
            if adj['cases_handled'] > 10:
                reason.append(f"Extensive experience ({int(adj['cases_handled'])} similar cases)")
            if adj['avg_days'] < df['SETTLEMENT_DAYS'].mean():
                reason.append(f"Faster settlement time")

            recommendations.append({
                "adjuster": adj['adjuster'],
                "overall_performance": float(adj['overall_performance']),
                "accuracy_rate": float(adj['accuracy_rate']),
                "consistency_score": float(adj['consistency_score']),
                "avg_settlement_days": float(adj['avg_days']),
                "cases_handled": int(adj['cases_handled']),
                "reasons": reason if reason else ["Adequate performance"]
            })

        return {
            "claim_id": claim_id,
            "current_adjuster": claim_data['adjuster'],
            "current_variance_pct": float(claim_data['variance_pct']),
            "injury_group": claim_data['INJURY_GROUP_CODE'],
            "severity_score": float(claim_data['SEVERITY_SCORE']),
            "recommended_adjusters": recommendations,
            "similar_cases_analyzed": len(similar_cases)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting adjuster recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/injury-benchmarks")
async def get_injury_benchmarks(
    injury_group: Optional[str] = Query(None, description="Filter by injury group")
):
    """
    Get benchmark statistics for injury groups
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)

        if injury_group:
            df = df[df['INJURY_GROUP_CODE'] == injury_group]

        # Group by injury and body part
        benchmarks = df.groupby(['INJURY_GROUP_CODE', 'PRIMARY_INJURY', 'PRIMARY_BODYPART']).agg({
            'claim_id': 'count',
            'DOLLARAMOUNTHIGH': ['mean', 'median', 'std', 'min', 'max'],
            'variance_pct': ['mean', 'std'],
            'SETTLEMENT_DAYS': 'mean',
            'SEVERITY_SCORE': 'mean'
        }).reset_index()

        benchmarks.columns = [
            'injury_group', 'injury_type', 'body_part', 'case_count',
            'avg_settlement', 'median_settlement', 'std_settlement', 'min_settlement', 'max_settlement',
            'avg_variance', 'std_variance', 'avg_days', 'avg_severity'
        ]

        # Calculate percentiles
        benchmarks['p25_settlement'] = benchmarks.apply(
            lambda row: df[
                (df['INJURY_GROUP_CODE'] == row['injury_group']) &
                (df['PRIMARY_INJURY'] == row['injury_type']) &
                (df['PRIMARY_BODYPART'] == row['body_part'])
            ]['DOLLARAMOUNTHIGH'].quantile(0.25), axis=1
        )

        benchmarks['p75_settlement'] = benchmarks.apply(
            lambda row: df[
                (df['INJURY_GROUP_CODE'] == row['injury_group']) &
                (df['PRIMARY_INJURY'] == row['injury_type']) &
                (df['PRIMARY_BODYPART'] == row['body_part'])
            ]['DOLLARAMOUNTHIGH'].quantile(0.75), axis=1
        )

        # Filter combinations with at least 3 cases
        benchmarks = benchmarks[benchmarks['case_count'] >= 3]

        return {
            "total_combinations": len(benchmarks),
            "benchmarks": benchmarks.to_dict('records')
        }

    except Exception as e:
        logger.error(f"Error getting injury benchmarks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variance-drivers")
async def get_variance_drivers():
    """
    Identify key factors driving variance in predictions
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)

        # Analyze categorical factors
        categorical_factors = [
            'INJURY_GROUP_CODE', 'PRIMARY_INJURY', 'CAUTION_LEVEL',
            'VENUE_RATING', 'VENUESTATE', 'PRIMARY_BODYPART'
        ]

        variance_by_factor = []

        for factor in categorical_factors:
            if factor in df.columns:
                factor_variance = df.groupby(factor)['variance_pct'].agg(['mean', 'std', 'count'])
                factor_variance = factor_variance[factor_variance['count'] >= 5]  # Minimum 5 cases

                for value, row in factor_variance.iterrows():
                    variance_by_factor.append({
                        "factor": factor,
                        "value": str(value),
                        "avg_variance_pct": float(row['mean']),
                        "std_variance": float(row['std']),
                        "case_count": int(row['count']),
                        "impact_score": float(abs(row['mean']) * row['count'] / 100)  # Weighted impact
                    })

        # Sort by impact score
        variance_by_factor = sorted(variance_by_factor, key=lambda x: x['impact_score'], reverse=True)

        return {
            "total_factors_analyzed": len(variance_by_factor),
            "top_variance_drivers": variance_by_factor[:20]
        }

    except Exception as e:
        logger.error(f"Error analyzing variance drivers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bad-combinations")
async def get_bad_combinations(
    min_variance_pct: float = Query(15.0, description="Minimum average variance to flag as 'bad'"),
    min_cases: int = Query(3, description="Minimum cases for combination to be considered")
):
    """
    Identify injury/body part combinations with consistently high variance
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)

        # Group by injury and body part combinations
        combinations = df.groupby(['INJURY_GROUP_CODE', 'PRIMARY_INJURY', 'PRIMARY_BODYPART']).agg({
            'claim_id': 'count',
            'variance_pct': ['mean', 'std', 'median'],
            'DOLLARAMOUNTHIGH': 'mean',
            'SEVERITY_SCORE': 'mean'
        }).reset_index()

        combinations.columns = [
            'injury_group', 'injury_type', 'body_part', 'case_count',
            'avg_variance_pct', 'std_variance', 'median_variance',
            'avg_settlement', 'avg_severity'
        ]

        # Filter bad combinations
        bad_combos = combinations[
            (combinations['case_count'] >= min_cases) &
            (combinations['avg_variance_pct'].abs() >= min_variance_pct)
        ].copy()

        # Calculate risk score
        bad_combos['risk_score'] = (
            bad_combos['avg_variance_pct'].abs() * 0.6 +
            bad_combos['std_variance'] * 0.3 +
            (bad_combos['case_count'] / df['claim_id'].count() * 100) * 0.1
        )

        bad_combos = bad_combos.sort_values('risk_score', ascending=False)

        # Add risk level
        bad_combos['risk_level'] = pd.cut(
            bad_combos['risk_score'],
            bins=[0, 20, 40, 60, float('inf')],
            labels=['Moderate', 'High', 'Very High', 'Critical']
        )

        return {
            "total_bad_combinations": len(bad_combos),
            "combinations": bad_combos.to_dict('records')
        }

    except Exception as e:
        logger.error(f"Error identifying bad combinations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
