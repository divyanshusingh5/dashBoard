from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
import asyncio

from app.api.schemas import (
    ClaimsResponse,
    AggregatedData,
    KPIData,
    FilterOptions,
)
# Switch to SQLite data service for better performance
from app.services.data_service_sqlite import data_service_sqlite as data_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/claims", response_model=ClaimsResponse)
async def get_claims(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    injury_group: Optional[List[str]] = Query(None, description="Filter by injury groups"),
    adjuster: Optional[List[str]] = Query(None, description="Filter by adjusters"),
    state: Optional[List[str]] = Query(None, description="Filter by states"),
    year: Optional[List[int]] = Query(None, description="Filter by years"),
):
    """
    Get paginated claims with optional filters
    """
    try:
        filters = {}
        if injury_group:
            filters['injury_group'] = injury_group
        if adjuster:
            filters['adjuster'] = adjuster
        if state:
            filters['state'] = state
        if year:
            filters['year'] = year

        result = await data_service.get_paginated_claims(
            page=page,
            page_size=page_size,
            filters=filters if filters else None
        )

        return result

    except Exception as e:
        logger.error(f"Error getting claims: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/full")
async def get_full_claims():
    """
    Get all claims data (use with caution for large datasets)
    """
    try:
        import math
        claims = await data_service.get_full_claims_data()

        # Clean up NaN/inf values for JSON serialization
        cleaned_claims = []
        for claim in claims:
            cleaned_claim = {}
            for key, value in claim.items():
                if isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        cleaned_claim[key] = None
                    else:
                        cleaned_claim[key] = value
                else:
                    cleaned_claim[key] = value
            cleaned_claims.append(cleaned_claim)

        return {
            "claims": cleaned_claims,
            "total": len(cleaned_claims)
        }
    except Exception as e:
        logger.error(f"Error getting full claims: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# DEPRECATED: Aggregation moved to /api/v1/aggregation/aggregated
# This endpoint remains for backward compatibility but redirects internally
@router.get("/claims/aggregated")
async def get_aggregated_claims():
    """
    DEPRECATED: Use /api/v1/aggregation/aggregated instead
    This endpoint provides backward compatibility
    """
    from app.api.endpoints.aggregation import get_aggregated_data
    return await get_aggregated_data()

@router.get("/claims/kpis", response_model=KPIData)
async def get_kpis():
    """
    Get KPIs calculated from claims data
    """
    try:
        kpis = await data_service.calculate_kpis()
        return kpis
    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/filters", response_model=FilterOptions)
async def get_filter_options():
    """
    Get available filter options from data
    """
    try:
        options = await data_service.get_filter_options()
        return options
    except Exception as e:
        logger.error(f"Error getting filter options: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/stats")
async def get_claims_stats():
    """
    Get statistical summary of claims data
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            return {"error": "No data available"}

        import pandas as pd
        df = pd.DataFrame(claims)

        stats = {
            "total_claims": len(df),
            "numeric_columns": {},
            "categorical_columns": {}
        }

        # Numeric column stats
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            stats["numeric_columns"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max())
            }

        # Categorical column stats
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:10]:  # Limit to first 10
            stats["categorical_columns"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_values": df[col].value_counts().head(5).to_dict()
            }

        return stats

    except Exception as e:
        logger.error(f"Error getting claims stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claims/ssnb")
async def get_ssnb_data(
    limit: Optional[int] = Query(None, description="Limit number of records")
):
    """
    Get SSNB data for weight recalibration
    Returns float-based clinical factors for single injury analysis
    """
    try:
        loop = asyncio.get_event_loop()
        session = data_service.get_session()

        def query_db():
            from app.db.schema import SSNB
            query = session.query(SSNB)
            if limit:
                query = query.limit(limit)

            results = []
            for ssnb in query.all():
                results.append({
                    'CLAIMID': ssnb.CLAIMID,
                    'VERSIONID': ssnb.VERSIONID,
                    'EXPSR_NBR': ssnb.EXPSR_NBR,
                    'DOLLARAMOUNTHIGH': ssnb.DOLLARAMOUNTHIGH,
                    'CAUSATION_HIGH_RECOMMENDATION': ssnb.CAUSATION_HIGH_RECOMMENDATION,
                    'PRIMARY_SEVERITY_SCORE': ssnb.PRIMARY_SEVERITY_SCORE,
                    'PRIMARY_CAUSATION_SCORE': ssnb.PRIMARY_CAUSATION_SCORE,
                    'PRIMARY_INJURY': ssnb.PRIMARY_INJURY,
                    'PRIMARY_BODYPART': ssnb.PRIMARY_BODYPART,
                    'PRIMARY_INJURY_GROUP': ssnb.PRIMARY_INJURY_GROUP,
                    # Float clinical factors (NOT categorical strings)
                    'Causation_Compliance': ssnb.Causation_Compliance,
                    'Clinical_Findings': ssnb.Clinical_Findings,
                    'Consistent_Mechanism': ssnb.Consistent_Mechanism,
                    'Injury_Location': ssnb.Injury_Location,
                    'Movement_Restriction': ssnb.Movement_Restriction,
                    'Pain_Management': ssnb.Pain_Management,
                    'Prior_Treatment': ssnb.Prior_Treatment,
                    'Symptom_Timeline': ssnb.Symptom_Timeline,
                    'Treatment_Course': ssnb.Treatment_Course,
                    'Treatment_Delays': ssnb.Treatment_Delays,
                    'Treatment_Period_Considered': ssnb.Treatment_Period_Considered,
                    'Vehicle_Impact': ssnb.Vehicle_Impact,
                    # Venue and demographics
                    'VENUERATING': ssnb.VENUERATING,
                    'RATINGWEIGHT': ssnb.RATINGWEIGHT,
                    'VENUERATINGTEXT': ssnb.VENUERATINGTEXT,
                    'VENUERATINGPOINT': ssnb.VENUERATINGPOINT,
                    'AGE': ssnb.AGE,
                    'GENDER': ssnb.GENDER,
                    'HASATTORNEY': ssnb.HASATTORNEY,
                    'IOL': ssnb.IOL,
                    'ADJUSTERNAME': ssnb.ADJUSTERNAME,
                    'COUNTYNAME': ssnb.COUNTYNAME,
                    'VENUESTATE': ssnb.VENUESTATE,
                })
            return results

        result = await loop.run_in_executor(None, query_db)
        session.close()

        return {
            "ssnb_data": result,
            "total": len(result)
        }

    except Exception as e:
        logger.error(f"Error getting SSNB data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claims/prediction-variance")
async def get_prediction_variance_analysis(
    variance_threshold: Optional[float] = Query(50.0, description="Variance % threshold for bad predictions"),
    limit: Optional[int] = Query(1000, description="Limit number of records")
):
    """
    Analyze prediction variance to identify bad predictions
    Returns claims where model prediction significantly differs from actual settlement

    Helps identify:
    - Factor combinations where predictions are unreliable
    - Systematic biases in the model
    - Opportunities for model improvement
    """
    try:
        loop = asyncio.get_event_loop()

        def query_db():
            import sqlite3
            import math
            from pathlib import Path

            # Connect to database
            db_path = Path(__file__).parent.parent.parent / 'db' / 'claims_analytics.db'
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            # Query claims with high variance using raw SQL
            cursor = conn.execute('''
                SELECT
                    CLAIMID,
                    DOLLARAMOUNTHIGH,
                    CAUSATION_HIGH_RECOMMENDATION,
                    variance_pct,
                    PRIMARY_INJURY_BY_SEVERITY,
                    PRIMARY_BODYPART_BY_SEVERITY,
                    PRIMARY_INJURY_SEVERITY_SCORE,
                    PRIMARY_INJURY_BY_CAUSATION,
                    PRIMARY_BODYPART_BY_CAUSATION,
                    PRIMARY_INJURY_CAUSATION_SCORE,
                    CALCULATED_SEVERITY_SCORE,
                    CALCULATED_CAUSATION_SCORE,
                    Causation_Compliance,
                    Clinical_Findings,
                    Treatment_Course,
                    Symptom_Timeline,
                    Pain_Management,
                    Movement_Restriction,
                    VENUERATING,
                    IOL,
                    AGE,
                    HASATTORNEY,
                    ADJUSTERNAME,
                    COUNTYNAME,
                    VENUESTATE
                FROM claims
                WHERE variance_pct IS NOT NULL
                    AND DOLLARAMOUNTHIGH IS NOT NULL
                    AND CAUSATION_HIGH_RECOMMENDATION IS NOT NULL
                    AND ABS(variance_pct) >= ?
                LIMIT ?
            ''', (variance_threshold, limit))

            results = []
            for row in cursor.fetchall():
                # Convert row to dict and clean values
                def clean_value(val):
                    if val is None:
                        return None
                    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                        return None
                    return val

                variance = clean_value(row['variance_pct'])
                results.append({
                    'CLAIMID': row['CLAIMID'],
                    'DOLLARAMOUNTHIGH': clean_value(row['DOLLARAMOUNTHIGH']),
                    'CAUSATION_HIGH_RECOMMENDATION': clean_value(row['CAUSATION_HIGH_RECOMMENDATION']),
                    'variance_pct': variance,
                    'prediction_direction': 'Over' if variance and variance < 0 else 'Under',

                    # Multi-tier injury data
                    'PRIMARY_INJURY_BY_SEVERITY': row['PRIMARY_INJURY_BY_SEVERITY'],
                    'PRIMARY_BODYPART_BY_SEVERITY': row['PRIMARY_BODYPART_BY_SEVERITY'],
                    'PRIMARY_INJURY_SEVERITY_SCORE': clean_value(row['PRIMARY_INJURY_SEVERITY_SCORE']),
                    'PRIMARY_INJURY_BY_CAUSATION': row['PRIMARY_INJURY_BY_CAUSATION'],
                    'PRIMARY_BODYPART_BY_CAUSATION': row['PRIMARY_BODYPART_BY_CAUSATION'],
                    'PRIMARY_INJURY_CAUSATION_SCORE': clean_value(row['PRIMARY_INJURY_CAUSATION_SCORE']),

                    # Composite scores
                    'CALCULATED_SEVERITY_SCORE': clean_value(row['CALCULATED_SEVERITY_SCORE']),
                    'CALCULATED_CAUSATION_SCORE': clean_value(row['CALCULATED_CAUSATION_SCORE']),

                    # Key clinical factors for analysis
                    'Causation_Compliance': row['Causation_Compliance'],
                    'Clinical_Findings': row['Clinical_Findings'],
                    'Treatment_Course': row['Treatment_Course'],
                    'Symptom_Timeline': row['Symptom_Timeline'],
                    'Pain_Management': row['Pain_Management'],
                    'Movement_Restriction': row['Movement_Restriction'],

                    # Venue and demographics
                    'VENUERATING': row['VENUERATING'],
                    'IOL': row['IOL'],
                    'AGE': row['AGE'],
                    'HASATTORNEY': row['HASATTORNEY'],
                    'ADJUSTERNAME': row['ADJUSTERNAME'],
                    'COUNTYNAME': row['COUNTYNAME'],
                    'VENUESTATE': row['VENUESTATE'],
                })

            conn.close()
            return results

        result = await loop.run_in_executor(None, query_db)

        # Calculate summary statistics
        if result:
            import numpy as np
            variances = [abs(r['variance_pct']) for r in result if r['variance_pct'] is not None]
            over_predictions = sum(1 for r in result if r['prediction_direction'] == 'Over')
            under_predictions = sum(1 for r in result if r['prediction_direction'] == 'Under')

            summary = {
                'total_bad_predictions': len(result),
                'over_predictions': over_predictions,
                'under_predictions': under_predictions,
                'avg_variance_pct': float(np.mean(variances)) if variances else 0.0,
                'max_variance_pct': float(np.max(variances)) if variances else 0.0,
                'min_variance_pct': float(np.min(variances)) if variances else 0.0,
            }
        else:
            summary = {
                'total_bad_predictions': 0,
                'over_predictions': 0,
                'under_predictions': 0,
            }

        return {
            "bad_predictions": result,
            "summary": summary,
            "filters": {
                "variance_threshold": variance_threshold,
                "limit": limit
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing prediction variance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claims/factor-combinations")
async def get_factor_combination_analysis(
    variance_threshold: Optional[float] = Query(50.0, description="Variance % threshold")
):
    """
    Analyze factor combinations to identify patterns in bad predictions

    Returns:
    - Most problematic factor combinations
    - Frequency of each combination in bad predictions
    - Average variance for each combination
    - Recommendations for model improvement
    """
    try:
        loop = asyncio.get_event_loop()

        def query_db():
            import sqlite3
            from collections import defaultdict
            from pathlib import Path

            # Connect to database
            db_path = Path(__file__).parent.parent.parent / 'db' / 'claims_analytics.db'
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            # Query claims with high variance using raw SQL
            cursor = conn.execute('''
                SELECT
                    CLAIMID,
                    variance_pct,
                    PRIMARY_INJURY_BY_SEVERITY,
                    PRIMARY_INJURY_BY_CAUSATION,
                    VENUERATING,
                    HASATTORNEY,
                    IOL,
                    Causation_Compliance,
                    Clinical_Findings,
                    DOLLARAMOUNTHIGH,
                    CAUSATION_HIGH_RECOMMENDATION
                FROM claims
                WHERE variance_pct IS NOT NULL
                    AND DOLLARAMOUNTHIGH IS NOT NULL
                    AND ABS(variance_pct) >= ?
            ''', (variance_threshold,))

            # Collect factor combinations
            factor_stats = defaultdict(lambda: {
                'count': 0,
                'total_variance': 0,
                'max_variance': 0,
                'claims': []
            })

            for row in cursor.fetchall():
                variance = abs(row['variance_pct']) if row['variance_pct'] else 0

                # Create factor combination key
                factors = {
                    'injury_severity': row['PRIMARY_INJURY_BY_SEVERITY'] or 'Unknown',
                    'injury_causation': row['PRIMARY_INJURY_BY_CAUSATION'] or 'Unknown',
                    'venue': row['VENUERATING'] or 'Unknown',
                    'attorney': 'Yes' if str(row['HASATTORNEY']).lower() in ['1', 'yes', 'true'] else 'No',
                    'ioi': row['IOL'] if row['IOL'] else 0,
                    'causation_compliance': row['Causation_Compliance'] or 'Unknown',
                    'clinical_findings': row['Clinical_Findings'] or 'Unknown',
                }

                # Create key from factors
                combo_key = f"{factors['injury_severity']}|{factors['venue']}|{factors['attorney']}|IOL_{factors['ioi']}"

                factor_stats[combo_key]['count'] += 1
                factor_stats[combo_key]['total_variance'] += variance
                factor_stats[combo_key]['max_variance'] = max(
                    factor_stats[combo_key]['max_variance'],
                    variance
                )
                factor_stats[combo_key]['factors'] = factors

                if len(factor_stats[combo_key]['claims']) < 5:
                    factor_stats[combo_key]['claims'].append({
                        'CLAIMID': row['CLAIMID'],
                        'variance_pct': variance,
                        'actual': row['DOLLARAMOUNTHIGH'],
                        'predicted': row['CAUSATION_HIGH_RECOMMENDATION']
                    })

            conn.close()

            # Convert to sorted list
            combinations = []
            for combo_key, stats in factor_stats.items():
                if stats['count'] >= 3:  # Only include combinations with 3+ occurrences
                    avg_variance = stats['total_variance'] / stats['count']
                    combinations.append({
                        'combination_key': combo_key,
                        'factors': stats['factors'],
                        'count': stats['count'],
                        'avg_variance_pct': round(avg_variance, 2),
                        'max_variance_pct': round(stats['max_variance'], 2),
                        'sample_claims': stats['claims']
                    })

            # Sort by count (most frequent first)
            combinations.sort(key=lambda x: x['count'], reverse=True)

            return combinations[:50]  # Top 50 combinations

        result = await loop.run_in_executor(None, query_db)

        return {
            "problematic_combinations": result,
            "total_combinations": len(result),
            "filters": {
                "variance_threshold": variance_threshold,
                "min_occurrences": 3
            },
            "recommendations": [
                "Focus model improvements on high-frequency combinations",
                "Consider separate models for different injury/venue combinations",
                "Review clinical factor encoding for consistency",
                "Validate venue rating impact on predictions"
            ]
        }

    except Exception as e:
        logger.error(f"Error analyzing factor combinations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
