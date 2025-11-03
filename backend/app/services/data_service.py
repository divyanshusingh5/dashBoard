import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from functools import lru_cache
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class DataService:
    """Service for handling claims data operations"""

    def __init__(self):
        self.data_cache = {}

    async def load_csv_file(self, file_path: str) -> pd.DataFrame:
        """Load CSV file asynchronously"""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(None, pd.read_csv, file_path)
            logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            raise

    async def get_full_claims_data(self) -> List[Dict[str, Any]]:
        """Load full claims dataset"""
        try:
            df = await self.load_csv_file(settings.CSV_FILE_PATH)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting full claims data: {str(e)}")
            return []

    async def get_paginated_claims(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get paginated claims with optional filters"""
        try:
            df = await self.load_csv_file(settings.CSV_FILE_PATH)

            # Apply filters
            if filters:
                if filters.get('injury_group'):
                    df = df[df['InjuryGroup'].isin(filters['injury_group'])]
                if filters.get('adjuster'):
                    df = df[df['Adjuster'].isin(filters['adjuster'])]
                if filters.get('state'):
                    df = df[df['State'].isin(filters['state'])]
                if filters.get('year'):
                    df = df[df['SettlementYear'].isin(filters['year'])]

            total = len(df)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            paginated_df = df.iloc[start_idx:end_idx]

            return {
                "claims": paginated_df.to_dict('records'),
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            logger.error(f"Error getting paginated claims: {str(e)}")
            return {"claims": [], "total": 0, "page": page, "page_size": page_size}

    async def get_aggregated_data(self) -> Dict[str, Any]:
        """Load aggregated data from CSV files"""
        try:
            data_dir = Path(settings.AGGREGATED_DATA_DIR)

            # Load aggregated files
            adjuster_agg = await self.load_csv_file(str(data_dir / "adjuster_aggregated.csv"))
            injury_agg = await self.load_csv_file(str(data_dir / "injury_aggregated.csv"))
            state_agg = await self.load_csv_file(str(data_dir / "state_aggregated.csv"))
            county_agg = await self.load_csv_file(str(data_dir / "county_aggregated.csv"))
            year_agg = await self.load_csv_file(str(data_dir / "year_aggregated.csv"))

            return {
                "adjuster": adjuster_agg.to_dict('records'),
                "injury": injury_agg.to_dict('records'),
                "state": state_agg.to_dict('records'),
                "county": county_agg.to_dict('records'),
                "year": year_agg.to_dict('records'),
                "total_records": len(adjuster_agg) + len(injury_agg) + len(state_agg) + len(county_agg) + len(year_agg)
            }
        except Exception as e:
            logger.error(f"Error loading aggregated data: {str(e)}")
            return {"adjuster": [], "injury": [], "state": [], "county": [], "year": [], "total_records": 0}

    async def calculate_kpis(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Calculate KPIs from claims data"""
        try:
            if df is None:
                df = await self.load_csv_file(settings.CSV_FILE_PATH)

            total_claims = len(df)
            total_settlement = df['SettlementAmount'].sum()
            avg_settlement = df['SettlementAmount'].mean()
            median_settlement = df['SettlementAmount'].median()

            # Calculate variance metrics
            df['Variance'] = df['ModelPrediction'] - df['ConsensusValue']
            df['VariancePct'] = (df['Variance'] / df['ConsensusValue']) * 100

            avg_variance = df['Variance'].mean()
            avg_variance_pct = df['VariancePct'].mean()

            total_overestimated = df[df['Variance'] > 0]['Variance'].sum()
            total_underestimated = abs(df[df['Variance'] < 0]['Variance'].sum())

            return {
                "total_claims": int(total_claims),
                "total_settlement": float(total_settlement),
                "avg_settlement": float(avg_settlement),
                "avg_variance": float(avg_variance),
                "avg_variance_pct": float(avg_variance_pct),
                "median_settlement": float(median_settlement),
                "total_overestimated": float(total_overestimated),
                "total_underestimated": float(total_underestimated)
            }
        except Exception as e:
            logger.error(f"Error calculating KPIs: {str(e)}")
            return {}

    async def get_filter_options(self) -> Dict[str, List[Any]]:
        """Get available filter options from data"""
        try:
            df = await self.load_csv_file(settings.CSV_FILE_PATH)

            return {
                "injury_groups": sorted(df['InjuryGroup'].dropna().unique().tolist()),
                "adjusters": sorted(df['Adjuster'].dropna().unique().tolist()),
                "states": sorted(df['State'].dropna().unique().tolist()),
                "counties": sorted(df['County'].dropna().unique().tolist()),
                "years": sorted(df['SettlementYear'].dropna().unique().tolist())
            }
        except Exception as e:
            logger.error(f"Error getting filter options: {str(e)}")
            return {"injury_groups": [], "adjusters": [], "states": [], "counties": [], "years": []}

# Singleton instance
data_service = DataService()
