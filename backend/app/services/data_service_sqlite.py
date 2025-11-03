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
                query = session.query(Claim)
                if limit:
                    query = query.limit(limit)
                return [self._claim_to_dict(claim) for claim in query.all()]

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

                # Apply filters
                if filters:
                    if filters.get('injury_group'):
                        query = query.filter(Claim.INJURY_GROUP_CODE.in_(filters['injury_group']))
                    if filters.get('adjuster'):
                        query = query.filter(Claim.adjuster.in_(filters['adjuster']))
                    if filters.get('county'):
                        query = query.filter(Claim.COUNTYNAME.in_(filters['county']))
                    if filters.get('venue_rating'):
                        query = query.filter(Claim.VENUE_RATING.in_(filters['venue_rating']))
                    if filters.get('min_variance'):
                        query = query.filter(Claim.variance_pct >= filters['min_variance'])
                    if filters.get('max_variance'):
                        query = query.filter(Claim.variance_pct <= filters['max_variance'])
                    if filters.get('year'):
                        query = query.filter(Claim.claim_date.like(f"{filters['year']}%"))

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
                # Query pre-computed materialized views
                year_severity = session.execute(
                    text("SELECT * FROM mv_year_severity ORDER BY year DESC, severity_category")
                ).fetchall()

                county_year = session.execute(
                    text("SELECT * FROM mv_county_year ORDER BY year DESC, claim_count DESC")
                ).fetchall()

                injury_group = session.execute(
                    text("SELECT * FROM mv_injury_group ORDER BY claim_count DESC")
                ).fetchall()

                adjuster_perf = session.execute(
                    text("SELECT * FROM mv_adjuster_performance ORDER BY claim_count DESC")
                ).fetchall()

                venue_analysis = session.execute(
                    text("SELECT * FROM mv_venue_analysis ORDER BY claim_count DESC")
                ).fetchall()

                # Convert to dictionaries (exclude id and created_at columns)
                def row_to_dict(row):
                    d = dict(row._mapping)
                    d.pop('id', None)
                    d.pop('created_at', None)
                    return d

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
                # Try to get from materialized view first
                result = session.execute(
                    text("SELECT * FROM mv_kpi_summary ORDER BY created_at DESC LIMIT 1")
                ).fetchone()

                if result:
                    d = dict(result._mapping)
                    return {
                        "totalClaims": int(d.get('total_claims', 0)),
                        "avgSettlement": round(float(d.get('avg_settlement', 0)), 2),
                        "avgDays": round(float(d.get('avg_days', 0)), 2),
                        "highVariancePct": round(float(d.get('high_variance_pct', 0)), 2),
                        "overpredictionRate": round(float(d.get('overprediction_rate', 0)), 2),
                        "underpredictionRate": round(float(d.get('underprediction_rate', 0)), 2)
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
        """Convert Claim object to dictionary"""
        return {
            'claim_id': claim.claim_id,
            'VERSIONID': claim.VERSIONID,
            'claim_date': claim.claim_date,
            'DURATIONTOREPORT': claim.DURATIONTOREPORT,
            'DOLLARAMOUNTHIGH': claim.DOLLARAMOUNTHIGH,
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
            'SETTLEMENT_DAYS': claim.SETTLEMENT_DAYS,
            'SETTLEMENT_MONTHS': claim.SETTLEMENT_MONTHS,
            'SETTLEMENT_YEARS': claim.SETTLEMENT_YEARS,
            'IMPACT': claim.IMPACT,
            'COUNTYNAME': claim.COUNTYNAME,
            'VENUESTATE': claim.VENUESTATE,
            'VENUE_RATING': claim.VENUE_RATING,
            'RATINGWEIGHT': claim.RATINGWEIGHT,
            'INJURY_GROUP_CODE': claim.INJURY_GROUP_CODE,
            'CAUSATION__HIGH_RECOMMENDATION': claim.CAUSATION__HIGH_RECOMMENDATION,
            'SEVERITY_SCORE': claim.SEVERITY_SCORE,
            'CAUTION_LEVEL': claim.CAUTION_LEVEL,
            'adjuster': claim.adjuster,
            'predicted_pain_suffering': claim.predicted_pain_suffering,
            'variance_pct': claim.variance_pct,
            'causation_probability': claim.causation_probability,
            'causation_tx_delay': claim.causation_tx_delay,
            'causation_tx_gaps': claim.causation_tx_gaps,
            # causation_compliance removed - duplicate of Causation_Compliance
            'severity_allowed_tx_period': claim.severity_allowed_tx_period,
            'severity_initial_tx': claim.severity_initial_tx,
            'severity_injections': claim.severity_injections,
            'severity_objective_findings': claim.severity_objective_findings,
            'severity_pain_mgmt': claim.severity_pain_mgmt,
            'severity_type_tx': claim.severity_type_tx,
            'severity_injury_site': claim.severity_injury_site,
            'severity_code': claim.severity_code,
            # Include all extended features as needed
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


# Singleton instance
data_service_sqlite = DataServiceSQLite()
