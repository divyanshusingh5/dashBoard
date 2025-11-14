"""
Data Service - SQLite Version
High-performance data access for 2M+ rows
Uses SQLite with indexes and optimized queries
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from functools import lru_cache
import logging
from sqlalchemy import func, case, and_, or_, desc, asc, text
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.db.schema import get_engine, get_session, Claim, Weight, AggregatedCache
from app.core.config import settings

logger = logging.getLogger(__name__)


class DataServiceSQLite:
    """Service for handling claims data operations using SQLite"""

    def __init__(self):
        self.engine = get_engine()
        self.data_cache = {}

    def get_session(self) -> Session:
        """Get database session"""
        return get_session(self.engine)

    async def get_full_claims_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load full claims dataset from SQLite
        For 2M+ rows, use pagination or filters
        """
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                try:
                    query = session.query(Claim)
                    if limit:
                        query = query.limit(limit)
                    return [self._claim_to_dict(claim) for claim in query.all()]
                except Exception as e:
                    logger.error(f"Database query failed: {str(e)}")
                    # Fallback to CSV if database is not properly initialized
                    return self._load_from_csv(limit)

            claims = await loop.run_in_executor(None, query_db)
            session.close()

            logger.info(f"Loaded {len(claims)} claims from database")
            return claims

        except Exception as e:
            logger.error(f"Error getting full claims data: {str(e)}")
            return []

    async def get_paginated_claims(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get paginated claims with filters and sorting
        Optimized for large datasets
        """
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                query = session.query(Claim)

                # Apply filters - UPDATED FOR ACTUAL COLUMN NAMES
                if filters:
                    if filters.get('injury_group'):
                        query = query.filter(Claim.PRIMARY_INJURYGROUP_CODE.in_(filters['injury_group']))
                    if filters.get('adjuster'):
                        query = query.filter(Claim.ADJUSTERNAME.in_(filters['adjuster']))
                    if filters.get('county'):
                        query = query.filter(Claim.COUNTYNAME.in_(filters['county']))
                    if filters.get('venue_rating'):
                        query = query.filter(Claim.VENUERATING.in_(filters['venue_rating']))
                    if filters.get('min_variance'):
                        query = query.filter(Claim.variance_pct >= filters['min_variance'])
                    if filters.get('max_variance'):
                        query = query.filter(Claim.variance_pct <= filters['max_variance'])
                    if filters.get('year'):
                        query = query.filter(Claim.CLAIMCLOSEDDATE.like(f"{filters['year']}%"))

                # Get total count before pagination
                total = query.count()

                # Apply sorting
                if sort_by:
                    column = getattr(Claim, sort_by, None)
                    if column:
                        if sort_order == "desc":
                            query = query.order_by(desc(column))
                        else:
                            query = query.order_by(asc(column))

                # Apply pagination
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)

                claims = [self._claim_to_dict(claim) for claim in query.all()]

                return {
                    "claims": claims,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size
                }

            result = await loop.run_in_executor(None, query_db)
            session.close()
            return result

        except Exception as e:
            logger.error(f"Error getting paginated claims: {str(e)}")
            return {"claims": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    async def get_aggregated_data(self) -> Dict[str, Any]:
        """
        Get aggregated data for dashboard
        Uses optimized SQL queries instead of loading full dataset
        LEGACY METHOD - Use get_aggregated_data_fast() for better performance
        """
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                # County-Year aggregation
                county_year = session.query(
                    Claim.COUNTYNAME.label('county'),
                    func.substr(Claim.claim_date, 1, 4).label('year'),
                    func.count(Claim.id).label('claim_count'),
                    func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
                    func.avg(Claim.variance_pct).label('avg_variance_pct'),
                    func.avg(Claim.SETTLEMENT_DAYS).label('avg_days')
                ).filter(
                    Claim.COUNTYNAME.isnot(None),
                    Claim.claim_date.isnot(None)
                ).group_by(
                    Claim.COUNTYNAME,
                    func.substr(Claim.claim_date, 1, 4)
                ).all()

                # Year-Severity aggregation
                year_severity = session.query(
                    func.substr(Claim.claim_date, 1, 4).label('year'),
                    case(
                        (Claim.SEVERITY_SCORE <= 4, 'Low'),
                        (Claim.SEVERITY_SCORE <= 8, 'Medium'),
                        else_='High'
                    ).label('severity_category'),
                    func.count(Claim.id).label('claim_count'),
                    func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
                    func.avg(Claim.variance_pct).label('avg_variance_pct')
                ).filter(
                    Claim.claim_date.isnot(None),
                    Claim.SEVERITY_SCORE.isnot(None)
                ).group_by(
                    func.substr(Claim.claim_date, 1, 4),
                    case(
                        (Claim.SEVERITY_SCORE <= 4, 'Low'),
                        (Claim.SEVERITY_SCORE <= 8, 'Medium'),
                        else_='High'
                    )
                ).all()

                # Injury Group aggregation
                injury_group = session.query(
                    Claim.INJURY_GROUP_CODE.label('injury_group'),
                    func.count(Claim.id).label('claim_count'),
                    func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
                    func.avg(Claim.variance_pct).label('avg_variance_pct')
                ).filter(
                    Claim.INJURY_GROUP_CODE.isnot(None)
                ).group_by(
                    Claim.INJURY_GROUP_CODE
                ).all()

                # Venue Analysis
                venue_analysis = session.query(
                    Claim.COUNTYNAME.label('county'),
                    Claim.VENUESTATE.label('venue_state'),
                    Claim.VENUE_RATING.label('current_rating'),
                    func.count(Claim.id).label('claim_count'),
                    func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
                    func.avg(Claim.variance_pct).label('avg_variance_pct')
                ).filter(
                    Claim.COUNTYNAME.isnot(None)
                ).group_by(
                    Claim.COUNTYNAME,
                    Claim.VENUESTATE,
                    Claim.VENUE_RATING
                ).all()

                # Adjuster Performance
                adjuster_performance = session.query(
                    Claim.adjuster,
                    func.count(Claim.id).label('claim_count'),
                    func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
                    func.avg(Claim.variance_pct).label('avg_variance_pct'),
                    func.avg(Claim.SETTLEMENT_DAYS).label('avg_days')
                ).filter(
                    Claim.adjuster.isnot(None)
                ).group_by(
                    Claim.adjuster
                ).all()

                return {
                    'countyYear': [dict(row._mapping) for row in county_year],
                    'yearSeverity': [dict(row._mapping) for row in year_severity],
                    'injuryGroup': [dict(row._mapping) for row in injury_group],
                    'venueAnalysis': [dict(row._mapping) for row in venue_analysis],
                    'adjusterPerformance': [dict(row._mapping) for row in adjuster_performance]
                }

            result = await loop.run_in_executor(None, query_db)
            session.close()

            logger.info("Generated aggregated data from database")
            return result

        except Exception as e:
            logger.error(f"Error getting aggregated data: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'countyYear': [],
                'yearSeverity': [],
                'injuryGroup': [],
                'venueAnalysis': [],
                'adjusterPerformance': []
            }

    async def get_aggregated_data_fast(self) -> Dict[str, Any]:
        """
        Get aggregated data from materialized views
        60x faster than computing from raw claims for 5M+ records

        Returns pre-computed aggregations from materialized view tables
        """
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                # Query pre-computed PostgreSQL materialized views
                year_severity = session.execute(
                    text("SELECT * FROM mv_year_severity ORDER BY year DESC, severity_category")
                ).fetchall()

                county_year = session.execute(
                    text("SELECT * FROM mv_county_year ORDER BY year DESC, claim_count DESC")
                ).fetchall()

                injury_group = session.execute(
                    text("SELECT * FROM mv_injury_group ORDER BY claim_count DESC")
                ).fetchall()

                # Note: mv_adjuster_performance uses 'total_claims' not 'claim_count'
                adjuster_perf = session.execute(
                    text("SELECT * FROM mv_adjuster_performance ORDER BY total_claims DESC")
                ).fetchall()

                venue_analysis = session.execute(
                    text("SELECT * FROM mv_venue_analysis ORDER BY claim_count DESC")
                ).fetchall()

                # Convert to dictionaries (PostgreSQL views don't have id/created_at)
                def row_to_dict(row):
                    return dict(row._mapping)

                return {
                    'yearSeverity': [row_to_dict(row) for row in year_severity],
                    'countyYear': [row_to_dict(row) for row in county_year],
                    'injuryGroup': [row_to_dict(row) for row in injury_group],
                    'adjusterPerformance': [row_to_dict(row) for row in adjuster_perf],
                    'venueAnalysis': [row_to_dict(row) for row in venue_analysis]
                }

            result = await loop.run_in_executor(None, query_db)
            session.close()

            logger.info("Retrieved aggregated data from materialized views (FAST)")
            return result

        except Exception as e:
            logger.error(f"Error getting aggregated data from materialized views: {str(e)}")
            logger.warning("Falling back to slow aggregation method...")
            # Fallback to slow method if materialized views don't exist
            return await self.get_aggregated_data()

    async def get_kpis_fast(self) -> Dict[str, Any]:
        """
        Get KPIs from materialized view
        Much faster than calculating from all claims
        """
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                # Get aggregated KPIs from PostgreSQL materialized view
                # Note: PostgreSQL view has year/month columns, get most recent or aggregate all
                result = session.execute(
                    text("SELECT * FROM mv_kpi_summary ORDER BY year DESC, month DESC LIMIT 1")
                ).fetchone()

                if result:
                    d = dict(result._mapping)
                    return {
                        "totalClaims": int(d.get('total_claims', 0)),
                        "avgSettlement": round(float(d.get('avg_settlement', 0)), 2),
                        "avgDays": round(float(d.get('avg_settlement_days', 0)), 2),
                        "highVariancePct": round(float(d.get('avg_variance_pct', 0)), 2),
                        "accuracyRate": round(float(d.get('accuracy_rate', 0)), 2),
                        "medianSettlement": round(float(d.get('median_settlement', 0)), 2)
                    }
                else:
                    # Fallback to computing directly
                    return None

            result = await loop.run_in_executor(None, query_db)
            session.close()

            if result:
                logger.info("Retrieved KPIs from materialized view (FAST)")
                return result
            else:
                logger.warning("No KPI data in materialized view, computing from claims...")
                return await self.get_kpis()

        except Exception as e:
            logger.error(f"Error getting KPIs from materialized view: {str(e)}")
            # Fallback to slow method
            return await self.get_kpis()

    async def get_kpis(self) -> Dict[str, Any]:
        """
        Calculate KPIs from database
        Optimized SQL aggregation
        """
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                stats = session.query(
                    func.count(Claim.id).label('total_claims'),
                    func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
                    func.avg(Claim.SETTLEMENT_DAYS).label('avg_days'),
                    func.avg(func.abs(Claim.variance_pct)).label('avg_variance')
                ).first()

                high_variance_count = session.query(func.count(Claim.id)).filter(
                    func.abs(Claim.variance_pct) >= 15
                ).scalar()

                overprediction_count = session.query(func.count(Claim.id)).filter(
                    Claim.variance_pct < 0
                ).scalar()

                underprediction_count = session.query(func.count(Claim.id)).filter(
                    Claim.variance_pct > 0
                ).scalar()

                total_claims = stats.total_claims or 1  # Avoid division by zero

                return {
                    "totalClaims": stats.total_claims or 0,
                    "avgSettlement": round(stats.avg_settlement or 0, 2),
                    "avgDays": round(stats.avg_days or 0, 2),
                    "highVariancePct": round((high_variance_count / total_claims) * 100, 2),
                    "overpredictionRate": round((overprediction_count / total_claims) * 100, 2),
                    "underpredictionRate": round((underprediction_count / total_claims) * 100, 2)
                }

            result = await loop.run_in_executor(None, query_db)
            session.close()
            return result

        except Exception as e:
            logger.error(f"Error calculating KPIs: {str(e)}")
            return {
                "totalClaims": 0,
                "avgSettlement": 0,
                "avgDays": 0,
                "highVariancePct": 0,
                "overpredictionRate": 0,
                "underpredictionRate": 0
            }

    async def get_weights(self) -> List[Dict[str, Any]]:
        """Get all weights from database"""
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def query_db():
                weights = session.query(Weight).all()
                return [self._weight_to_dict(weight) for weight in weights]

            result = await loop.run_in_executor(None, query_db)
            session.close()
            return result

        except Exception as e:
            logger.error(f"Error getting weights: {str(e)}")
            return []

    async def update_weight(self, factor_name: str, new_weight: float) -> bool:
        """Update a weight value"""
        try:
            loop = asyncio.get_event_loop()
            session = self.get_session()

            def update_db():
                weight = session.query(Weight).filter(Weight.factor_name == factor_name).first()
                if weight:
                    weight.base_weight = new_weight
                    session.commit()
                    return True
                return False

            result = await loop.run_in_executor(None, update_db)
            session.close()
            return result

        except Exception as e:
            logger.error(f"Error updating weight: {str(e)}")
            return False

    def _claim_to_dict(self, claim: Claim) -> Dict[str, Any]:
        """Convert Claim object to dictionary - UPDATED FOR ACTUAL SCHEMA"""
        return {
            # Core identifiers
            'CLAIMID': claim.CLAIMID,
            'EXPSR_NBR': claim.EXPSR_NBR,

            # Dates
            'CLAIMCLOSEDDATE': claim.CLAIMCLOSEDDATE,
            'INCIDENTDATE': claim.INCIDENTDATE,

            # Financial
            'CAUSATION_HIGH_RECOMMENDATION': claim.CAUSATION_HIGH_RECOMMENDATION,
            'SETTLEMENTAMOUNT': claim.SETTLEMENTAMOUNT,
            'DOLLARAMOUNTHIGH': claim.DOLLARAMOUNTHIGH,
            'GENERALS': claim.GENERALS,

            # Version and duration
            'VERSIONID': claim.VERSIONID,
            'DURATIONTOREPORT': claim.DURATIONTOREPORT,

            # Person info
            'ADJUSTERNAME': claim.ADJUSTERNAME,
            'HASATTORNEY': claim.HASATTORNEY,
            'AGE': claim.AGE,
            'GENDER': claim.GENDER,
            'OCCUPATION_AVAILABLE': claim.OCCUPATION_AVAILABLE,
            'OCCUPATION': claim.OCCUPATION,

            # Injury info
            'ALL_BODYPARTS': claim.ALL_BODYPARTS,
            'ALL_INJURIES': claim.ALL_INJURIES,
            'ALL_INJURYGROUP_CODES': claim.ALL_INJURYGROUP_CODES,
            'ALL_INJURYGROUP_TEXTS': claim.ALL_INJURYGROUP_TEXTS,
            'PRIMARY_INJURY': claim.PRIMARY_INJURY,
            'PRIMARY_BODYPART': claim.PRIMARY_BODYPART,
            'PRIMARY_INJURYGROUP_CODE': claim.PRIMARY_INJURYGROUP_CODE,
            'INJURY_COUNT': claim.INJURY_COUNT,
            'BODYPART_COUNT': claim.BODYPART_COUNT,
            'INJURYGROUP_COUNT': claim.INJURYGROUP_COUNT,
            'BODY_REGION': claim.BODY_REGION,

            # Settlement timing
            'SETTLEMENT_DAYS': claim.SETTLEMENT_DAYS,
            'SETTLEMENT_MONTHS': claim.SETTLEMENT_MONTHS,
            'SETTLEMENT_YEARS': claim.SETTLEMENT_YEARS,
            'SETTLEMENT_SPEED_CATEGORY': claim.SETTLEMENT_SPEED_CATEGORY,

            # Location and venue
            'IOL': claim.IOL,
            'COUNTYNAME': claim.COUNTYNAME,
            'VENUESTATE': claim.VENUESTATE,
            'VENUERATINGTEXT': claim.VENUERATINGTEXT,
            'VENUERATINGPOINT': claim.VENUERATINGPOINT,
            'RATINGWEIGHT': claim.RATINGWEIGHT,
            'VENUERATING': claim.VENUERATING,
            'VULNERABLECLAIMANT': claim.VULNERABLECLAIMANT,

            # Calculated fields
            'SEVERITY_SCORE': claim.SEVERITY_SCORE,
            'CAUTION_LEVEL': claim.CAUTION_LEVEL,
            'variance_pct': claim.variance_pct,

            # NEW: Composite calculated scores
            'CALCULATED_SEVERITY_SCORE': claim.CALCULATED_SEVERITY_SCORE,
            'CALCULATED_CAUSATION_SCORE': claim.CALCULATED_CAUSATION_SCORE,
            'RN': claim.RN,

            # NEW: Multi-tier injury system - By SEVERITY
            'PRIMARY_INJURY_BY_SEVERITY': claim.PRIMARY_INJURY_BY_SEVERITY,
            'PRIMARY_BODYPART_BY_SEVERITY': claim.PRIMARY_BODYPART_BY_SEVERITY,
            'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY': claim.PRIMARY_INJURYGROUP_CODE_BY_SEVERITY,
            'PRIMARY_INJURY_SEVERITY_SCORE': claim.PRIMARY_INJURY_SEVERITY_SCORE,
            'PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY': claim.PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY,

            'SECONDARY_INJURY_BY_SEVERITY': claim.SECONDARY_INJURY_BY_SEVERITY,
            'SECONDARY_BODYPART_BY_SEVERITY': claim.SECONDARY_BODYPART_BY_SEVERITY,
            'SECONDARY_INJURYGROUP_CODE_BY_SEVERITY': claim.SECONDARY_INJURYGROUP_CODE_BY_SEVERITY,
            'SECONDARY_INJURY_SEVERITY_SCORE': claim.SECONDARY_INJURY_SEVERITY_SCORE,
            'SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY': claim.SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY,

            'TERTIARY_INJURY_BY_SEVERITY': claim.TERTIARY_INJURY_BY_SEVERITY,
            'TERTIARY_BODYPART_BY_SEVERITY': claim.TERTIARY_BODYPART_BY_SEVERITY,
            'TERTIARY_INJURY_SEVERITY_SCORE': claim.TERTIARY_INJURY_SEVERITY_SCORE,
            'TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY': claim.TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY,

            # NEW: Multi-tier injury system - By CAUSATION
            'PRIMARY_INJURY_BY_CAUSATION': claim.PRIMARY_INJURY_BY_CAUSATION,
            'PRIMARY_BODYPART_BY_CAUSATION': claim.PRIMARY_BODYPART_BY_CAUSATION,
            'PRIMARY_INJURYGROUP_CODE_BY_CAUSATION': claim.PRIMARY_INJURYGROUP_CODE_BY_CAUSATION,
            'PRIMARY_INJURY_CAUSATION_SCORE': claim.PRIMARY_INJURY_CAUSATION_SCORE,
            'PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION': claim.PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION,

            'SECONDARY_INJURY_BY_CAUSATION': claim.SECONDARY_INJURY_BY_CAUSATION,
            'SECONDARY_BODYPART_BY_CAUSATION': claim.SECONDARY_BODYPART_BY_CAUSATION,
            'SECONDARY_INJURYGROUP_CODE_BY_CAUSATION': claim.SECONDARY_INJURYGROUP_CODE_BY_CAUSATION,
            'SECONDARY_INJURY_CAUSATION_SCORE': claim.SECONDARY_INJURY_CAUSATION_SCORE,
            'SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION': claim.SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION,

            'TERTIARY_INJURY_BY_CAUSATION': claim.TERTIARY_INJURY_BY_CAUSATION,
            'TERTIARY_BODYPART_BY_CAUSATION': claim.TERTIARY_BODYPART_BY_CAUSATION,
            'TERTIARY_INJURY_CAUSATION_SCORE': claim.TERTIARY_INJURY_CAUSATION_SCORE,
            'TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION': claim.TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION,

            # Clinical features (40+)
            'Advanced_Pain_Treatment': claim.Advanced_Pain_Treatment,
            'Causation_Compliance': claim.Causation_Compliance,
            'Clinical_Findings': claim.Clinical_Findings,
            'Cognitive_Symptoms': claim.Cognitive_Symptoms,
            'Complete_Disability_Duration': claim.Complete_Disability_Duration,
            'Concussion_Diagnosis': claim.Concussion_Diagnosis,
            'Consciousness_Impact': claim.Consciousness_Impact,
            'Consistent_Mechanism': claim.Consistent_Mechanism,
            'Dental_Procedure': claim.Dental_Procedure,
            'Dental_Treatment': claim.Dental_Treatment,
            'Dental_Visibility': claim.Dental_Visibility,
            'Emergency_Treatment': claim.Emergency_Treatment,
            'Fixation_Method': claim.Fixation_Method,
            'Head_Trauma': claim.Head_Trauma,
            'Immobilization_Used': claim.Immobilization_Used,
            'Injury_Count_Feature': claim.Injury_Count_Feature,
            'Injury_Extent': claim.Injury_Extent,
            'Injury_Laterality': claim.Injury_Laterality,
            'Injury_Location': claim.Injury_Location,
            'Injury_Type': claim.Injury_Type,
            'Mobility_Assistance': claim.Mobility_Assistance,
            'Movement_Restriction': claim.Movement_Restriction,
            'Nerve_Involvement': claim.Nerve_Involvement,
            'Pain_Management': claim.Pain_Management,
            'Partial_Disability_Duration': claim.Partial_Disability_Duration,
            'Physical_Symptoms': claim.Physical_Symptoms,
            'Physical_Therapy': claim.Physical_Therapy,
            'Prior_Treatment': claim.Prior_Treatment,
            'Recovery_Duration': claim.Recovery_Duration,
            'Repair_Type': claim.Repair_Type,
            'Respiratory_Issues': claim.Respiratory_Issues,
            'Soft_Tissue_Damage': claim.Soft_Tissue_Damage,
            'Special_Treatment': claim.Special_Treatment,
            'Surgical_Intervention': claim.Surgical_Intervention,
            'Symptom_Timeline': claim.Symptom_Timeline,
            'Treatment_Compliance': claim.Treatment_Compliance,
            'Treatment_Course': claim.Treatment_Course,
            'Treatment_Delays': claim.Treatment_Delays,
            'Treatment_Level': claim.Treatment_Level,
            'Treatment_Period_Considered': claim.Treatment_Period_Considered,
            'Vehicle_Impact': claim.Vehicle_Impact,
        }

    def _weight_to_dict(self, weight: Weight) -> Dict[str, Any]:
        """Convert Weight object to dictionary"""
        return {
            'factor_name': weight.factor_name,
            'base_weight': weight.base_weight,
            'min_weight': weight.min_weight,
            'max_weight': weight.max_weight,
            'category': weight.category,
            'description': weight.description
        }

    def _load_from_csv(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fallback method to load data from CSV when database is unavailable
        """
        try:
            csv_path = Path(__file__).parent.parent.parent / 'data' / 'dat.csv'
            logger.info(f"Loading data from CSV fallback: {csv_path}")

            df = pd.read_csv(csv_path)

            if limit:
                df = df.head(limit)

            # Replace NaN, inf, -inf with None for JSON serialization
            df = df.replace([np.nan, np.inf, -np.inf], None)

            # Convert DataFrame to list of dictionaries
            claims = df.to_dict('records')
            logger.info(f"Loaded {len(claims)} claims from CSV")
            return claims
        except Exception as e:
            logger.error(f"Failed to load from CSV: {str(e)}")
            return []


# Singleton instance
data_service_sqlite = DataServiceSQLite()
