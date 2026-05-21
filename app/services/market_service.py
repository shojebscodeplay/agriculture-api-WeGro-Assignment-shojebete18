import logging
from app.core.database import fetch_data
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def get_price_comparison(market_type=None, crop_category=None, year=None, season=None, price_tier=None, district=None):
    try:
        df = fetch_data("SELECT * FROM vw_harvest_full")

        if market_type:
            df = df[df["market_type"] == market_type]
        if crop_category:
            df = df[df["crop_category"] == crop_category]
        if year:
            df = df[df["year"] == year]
        if season:
            df = df[df["season"] == season]
        if price_tier:
            df = df[df["price_tier"] == price_tier]
        if district:
            df = df[df["farm_district"] == district]

        grouped = df.groupby(["market_name", "market_type", "price_tier", "farm_district", "crop_name"]).agg(
            avg_price_per_ton_bdt=("price_per_ton_bdt", "mean"),
            total_quantity_sold_ton=("quantity_sold_ton", "sum"),
            total_revenue_bdt=("revenue_bdt", "sum"),
        ).reset_index()

        grouped["avg_price_per_ton_bdt"] = grouped["avg_price_per_ton_bdt"].round(0)

        filters_applied = {}
        if market_type:
            filters_applied["market_type"] = market_type
        if crop_category:
            filters_applied["crop_category"] = crop_category
        if year:
            filters_applied["year"] = year
        if season:
            filters_applied["season"] = season
        if price_tier:
            filters_applied["price_tier"] = price_tier
        if district:
            filters_applied["district"] = district

        return {
            "filters_applied": filters_applied,
            "comparison": grouped[[
                "market_name", "market_type", "price_tier",
                "farm_district", "crop_name",
                "avg_price_per_ton_bdt", "total_quantity_sold_ton",
                "total_revenue_bdt"
            ]].rename(columns={
                "farm_district": "district"
            }).to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"get_price_comparison failed: {e}")
        raise DatabaseError(str(e))