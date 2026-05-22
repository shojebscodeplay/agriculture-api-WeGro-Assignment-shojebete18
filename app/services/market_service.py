import logging
from typing import Any, Dict
from app.core.database import fetch_data
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _extract_active_filters(**kwargs) -> Dict[str, Any]:
    """Helper function to remove None values and extract applied filters dynamically."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _build_sql_query(base_view: str, filters: Dict[str, Any]) -> tuple:
    if not filters:
        return f"SELECT * FROM {base_view}", {}
    
    conditions = []
    params = {}
    for key, value in filters.items():
        conditions.append(f"{key} = %({key})s")
        params[key] = value
        
    query = f"SELECT * FROM {base_view} WHERE {' AND '.join(conditions)}"
    return query, params

def get_price_comparison(market_type=None, crop_category=None, year=None, season=None, price_tier=None, district=None):
    try:
        filters_applied = _extract_active_filters(
            market_type=market_type, crop_category=crop_category, 
            year=year, season=season, price_tier=price_tier, district=district
        )

        sql_filters = {}
        for key, value in filters_applied.items():
            if key == "district":
                sql_filters["farm_district"] = value
            else:
                sql_filters[key] = value

        query, params = _build_sql_query("vw_harvest_full", sql_filters)
        df = fetch_data(query, params)

        if df.empty:
            return {
                "filters_applied": filters_applied,
                "comparison": []
            }

        grouped = df.groupby(["market_name", "market_type", "price_tier", "farm_district", "crop_name"]).agg(
            avg_price_per_ton_bdt=("price_per_ton_bdt", "mean"),
            total_quantity_sold_ton=("quantity_sold_ton", "sum"),
            total_revenue_bdt=("revenue_bdt", "sum"),
        ).reset_index()

        grouped["avg_price_per_ton_bdt"] = grouped["avg_price_per_ton_bdt"].round(0)

        comparison_data = grouped[[
            "market_name", "market_type", "price_tier",
            "farm_district", "crop_name",
            "avg_price_per_ton_bdt", "total_quantity_sold_ton",
            "total_revenue_bdt"
        ]].rename(columns={
            "farm_district": "district"
        }).to_dict(orient="records")

        return {
            "filters_applied": filters_applied,
            "comparison": comparison_data
        }

    except Exception as e:
        logger.error(f"get_price_comparison failed: {e}")
        raise DatabaseError(str(e))