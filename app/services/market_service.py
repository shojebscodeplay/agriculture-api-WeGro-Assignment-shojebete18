import logging
from app.core.database import fetch_data,_extract_active_filters, _build_sql_query
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

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
    
if __name__ == "__main__":
    result = get_price_comparison(district="Gazipur", year=2023)
    print(result)