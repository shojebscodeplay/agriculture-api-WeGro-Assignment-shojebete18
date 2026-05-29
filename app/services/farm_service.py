import logging
import pandas as pd
from app.core.database import fetch_data, _extract_active_filters, _build_sql_query
from app.core.exceptions import InvalidFilterError, DatabaseError, RecordNotFoundError

logger = logging.getLogger(__name__)

VALID_FILTERS = {
    "region": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Rangpur", "Barisal", "Mymensingh"],
    "farm_type": ["Small", "Medium", "Large", "Commercial"],
    "season": ["Spring", "Summer", "Autumn", "Winter"],
    "year": [2022, 2023, 2024],
}

def validate_filter(field: str, value: any) -> None:
    if value and value not in VALID_FILTERS[field]:
        raise InvalidFilterError(
            field=field,
            value=value,
            allowed=VALID_FILTERS[field]
        )


def get_farm_summary(region=None, farm_type=None, year=None, season=None):
    try:
        validate_filter("region", region)
        validate_filter("farm_type", farm_type)
        validate_filter("season", season)
        if year:
            validate_filter("year", year)

        filters_applied = _extract_active_filters(region=region, farm_type=farm_type, year=year, season=season)
        query, params = _build_sql_query("vw_harvest_full", filters_applied)
        df = fetch_data(query, params)

        if df.empty:
            return {"total_farms": 0, "filters_applied": filters_applied, "data": []}

        grouped = df.groupby(["farm_name", "region", "farm_type"]).agg(
            total_revenue_bdt=("revenue_bdt", "sum"),
            total_cost_bdt=("input_cost_bdt", "sum"),
            total_profit_bdt=("net_profit_bdt", "sum"),
            total_lost_ton=("quantity_lost_ton", "sum"),
            total_harvested_ton=("quantity_harvested_ton", "sum"),
        ).reset_index()

        grouped["avg_loss_pct"] = round(
            (grouped["total_lost_ton"] / grouped["total_harvested_ton"]) * 100, 2
        )

        result = grouped[[
            "farm_name", "region", "farm_type",
            "total_revenue_bdt", "total_cost_bdt",
            "total_profit_bdt", "avg_loss_pct"
        ]].to_dict(orient="records")

        return {
            "total_farms": len(result),
            "filters_applied": filters_applied,
            "data": result
        }

    except InvalidFilterError:
        raise
    except Exception as e:
        logger.error(f"get_farm_summary failed: {e}")
        raise DatabaseError(str(e))


def get_farm_performance(farm_id: int, year=None, crop_category=None, market_type=None):
    try:
        farm_df = fetch_data(f"SELECT farm_name, owner_name, region FROM dim_farm WHERE farm_id = {farm_id}")
        if farm_df.empty:
            raise RecordNotFoundError(resource="farm", identifier=farm_id)
        
        farm_row = farm_df.iloc[0]
        farm_name = farm_row["farm_name"]
        
        filters_applied = _extract_active_filters(year=year, crop_category=crop_category, market_type=market_type)
        
        sql_filters = {"farm_name": farm_name, **filters_applied}
        query, params = _build_sql_query("vw_harvest_full", sql_filters)
        df = fetch_data(query, params)

        performance = []
        if not df.empty:
            performance = df[[
                "crop_name", "year", "market_type",
                "quantity_sold_ton", "revenue_bdt",
                "net_profit_bdt", "quality_grade"
            ]].to_dict(orient="records")

        return {
            "farm_id": farm_id,
            "farm_name": farm_name,
            "owner": farm_row["owner_name"],
            "region": farm_row["region"],
            "filters_applied": filters_applied,
            "performance": performance
        }

    except RecordNotFoundError:
        raise
    except Exception as e:
        logger.error(f"get_farm_performance failed: {e}")
        raise DatabaseError(str(e))
    

def get_top_farms(metric="profit", region=None, farm_type=None, year=None, limit=10):
    try:
        filters_applied = _extract_active_filters(region=region, farm_type=farm_type, year=year)
        
        query, params = _build_sql_query("vw_harvest_full", filters_applied)
        df = fetch_data(query, params)

        if df.empty:
            return {"metric": metric, "filters_applied": {**filters_applied, "limit": limit}, "rankings": []}

        grouped = df.groupby(["farm_name", "region", "farm_type"]).agg(
            net_profit_bdt=("net_profit_bdt", "sum"),
            total_revenue_bdt=("revenue_bdt", "sum"),
            total_yield=("quantity_harvested_ton", "sum"),
        ).reset_index()


        metric_mapping = {
            "profit": "net_profit_bdt",
            "revenue": "total_revenue_bdt",
            "yield": "total_yield"
        }
        
        sort_column = metric_mapping.get(metric, "net_profit_bdt")
        grouped = grouped.sort_values(sort_column, ascending=False).head(limit)
        grouped["rank"] = range(1, len(grouped) + 1)

        filters_applied["limit"] = limit

        return {
            "metric": metric,
            "filters_applied": filters_applied,
            "rankings": grouped[[
                "rank", "farm_name", "region",
                "farm_type", "net_profit_bdt",
                "total_revenue_bdt"
            ]].to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"get_top_farms failed: {e}")
        raise DatabaseError(str(e))
    

def get_loss_analysis(region=None, year=None, season=None, quality_grade=None, crop_category=None):
    try:
        filters_applied = _extract_active_filters(
            region=region, year=year, season=season, 
            quality_grade=quality_grade, crop_category=crop_category
        )
        
        query, params = _build_sql_query("vw_harvest_full", filters_applied)
        df = fetch_data(query, params)

        if df.empty:
            return {
                "filters_applied": filters_applied,
                "summary": {"total_harvested_ton": 0, "total_lost_ton": 0, "overall_loss_pct": 0},
                "breakdown": []
            }

        grouped = df.groupby(
            ["region", "season", "crop_category", "quality_grade"]
        ).agg(
            total_harvested_ton=("quantity_harvested_ton", "sum"),
            total_lost_ton=("quantity_lost_ton", "sum")
        ).reset_index()

        grouped["overall_loss_pct"] = (
            grouped["total_lost_ton"] /
            grouped["total_harvested_ton"].replace(0, 1)
        ) * 100

        grouped["overall_loss_pct"] = grouped["overall_loss_pct"].round(2)

        total_harvested = grouped["total_harvested_ton"].sum()
        total_lost = grouped["total_lost_ton"].sum()

        summary_data = {
            "total_harvested_ton": round(total_harvested, 1),
            "total_lost_ton": round(total_lost, 1),
            "overall_loss_pct": round((total_lost / total_harvested) * 100, 2) if total_harvested > 0 else 0
        }

        return {
            "filters_applied": filters_applied,
            "summary": summary_data,
            "breakdown": grouped.to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"get_loss_analysis failed: {e}")
        raise DatabaseError(str(e))