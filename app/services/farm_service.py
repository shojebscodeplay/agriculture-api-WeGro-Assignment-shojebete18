import logging
import pandas as pd
from app.core.database import fetch_data
from app.core.exceptions import InvalidFilterError, DatabaseError, RecordNotFoundError

logger = logging.getLogger(__name__)

VALID_FILTERS = {
    "region": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Rangpur", "Barisal", "Mymensingh"],
    "farm_type": ["Small", "Medium", "Large", "Commercial"],
    "season": ["Spring", "Summer", "Autumn", "Winter"],
    "year": [2022, 2023, 2024],
}

def validate_filter(field: str, value):
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

        df = fetch_data("SELECT * FROM vw_harvest_full")

        if region:
            df = df[df["region"] == region]
        if farm_type:
            df = df[df["farm_type"] == farm_type]
        if year:
            df = df[df["year"] == year]
        if season:
            df = df[df["season"] == season]

        grouped = df.groupby(["farm_name", "region", "farm_type"]).agg(
            total_revenue_bdt=("revenue_bdt", "sum"),
            total_cost_bdt=("input_cost_bdt", "sum"),
            total_profit_bdt=("net_profit_bdt", "sum"),
            avg_loss_pct=("quantity_lost_ton", "mean"),
        ).reset_index()

        filters_applied = {}
        if region:
            filters_applied["region"] = region
        if farm_type:
            filters_applied["farm_type"] = farm_type
        if year:
            filters_applied["year"] = year
        if season:
            filters_applied["season"] = season

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
        farm_df = fetch_data(f"SELECT * FROM dim_farm WHERE farm_id = {farm_id}")
        if farm_df.empty:
            raise RecordNotFoundError(resource="farm", identifier=farm_id)
        
        farm_name = farm_df.iloc[0]["farm_name"]
        owner = farm_df.iloc[0]["owner_name"]
        region = farm_df.iloc[0]["region"]
        
        df = fetch_data(f"SELECT * FROM vw_harvest_full WHERE farm_name = '{farm_name}'")

        if year:
            df = df[df["year"] == year]
        if crop_category:
            df = df[df["crop_category"] == crop_category]
        if market_type:
            df = df[df["market_type"] == market_type]

        filters_applied = {}

        if year:
            filters_applied["year"] = year
        if crop_category:
            filters_applied["crop_category"] = crop_category
        if market_type:
            filters_applied["market_type"] = market_type

        performance = df[[
            "crop_name", "year", "market_type",
            "quantity_sold_ton", "revenue_bdt",
            "net_profit_bdt", "quality_grade"
        ]].to_dict(orient="records")

        return {
            "farm_id": farm_id,
            "farm_name": farm_name,
            "owner": owner,
            "region": region,
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
        df = fetch_data("SELECT * FROM vw_harvest_full")

        if year:
            df = df[df["year"] == year]

        grouped = df.groupby(["farm_name", "region", "farm_type"]).agg(
            net_profit_bdt=("net_profit_bdt", "sum"),
            total_revenue_bdt=("revenue_bdt", "sum"),
            total_yield=("quantity_harvested_ton", "sum"),
        ).reset_index()

        if region:
            grouped = grouped[grouped["region"] == region]
        if farm_type:
            grouped = grouped[grouped["farm_type"] == farm_type]

        if metric == "profit":
            grouped = grouped.sort_values("net_profit_bdt", ascending=False)
        elif metric == "revenue":
            grouped = grouped.sort_values("total_revenue_bdt", ascending=False)
        elif metric == "yield":
            grouped = grouped.sort_values("total_yield", ascending=False)

        grouped = grouped.head(limit)

        grouped["rank"] = range(1, len(grouped) + 1)

        filters_applied = {}
        if region:
            filters_applied["region"] = region
        if farm_type:
            filters_applied["farm_type"] = farm_type
        if year:
            filters_applied["year"] = year
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
        df = fetch_data("SELECT * FROM vw_harvest_full")

        if year:
            df = df[df["year"] == year]

        if region:
            df = df[df["region"] == region]

        if season:
            df = df[df["season"] == season]

        if quality_grade:
            df = df[df["quality_grade"] == quality_grade]

        if crop_category:
            df = df[df["crop_category"] == crop_category]

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
            "overall_loss_pct": round(
                (total_lost / total_harvested) * 100,
                2
            ) if total_harvested > 0 else 0
        }

        filters_applied = {}

        if region:
            filters_applied["region"] = region

        if year:
            filters_applied["year"] = year

        if season:
            filters_applied["season"] = season

        if quality_grade:
            filters_applied["quality_grade"] = quality_grade

        if crop_category:
            filters_applied["crop_category"] = crop_category

        return {
            "filters_applied": filters_applied,
            "summary": summary_data,
            "breakdown": grouped.to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"get_loss_analysis failed: {e}")
        raise DatabaseError(str(e))