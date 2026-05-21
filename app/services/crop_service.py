import logging
from app.core.database import fetch_data
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def get_yield_efficiency(region=None, crop_category=None, year=None, season=None, water_requirement=None):
    try:
        df = fetch_data("SELECT * FROM vw_harvest_full")
        crop_dim = fetch_data("SELECT * FROM dim_crop")
        df = df.merge(crop_dim, on="crop_name", how="left")

        if region:
            df = df[df["region"] == region]
        if year:
            df = df[df["year"] == year]
        if season:
            df = df[df["season"] == season]
        if crop_category:
            df = df[df["crop_category_x"] == crop_category]
        if water_requirement:
            df = df[df["water_requirement"] == water_requirement]

        grouped = df.groupby(["crop_name", "crop_category_x"]).agg(
            total_harvested=("quantity_harvested_ton", "sum"),
            total_area=("area_planted_ha", "sum"),
            benchmark=("avg_yield_ton_per_ha", "first"),
            season=("season", "first"),
        ).reset_index()

        grouped["actual_avg_yield_ton_per_ha"] = round(grouped["total_harvested"] / grouped["total_area"], 2)
        grouped["efficiency_pct"] = round((grouped["actual_avg_yield_ton_per_ha"] / grouped["benchmark"]) * 100, 1)

        filters_applied = {}
        if region:
            filters_applied["region"] = region
        if year:
            filters_applied["year"] = year
        if season:
            filters_applied["season"] = season
        if crop_category:
            filters_applied["crop_category"] = crop_category
        if water_requirement:
            filters_applied["water_requirement"] = water_requirement

        data = grouped[[
            "crop_name", "crop_category_x",
            "benchmark", "actual_avg_yield_ton_per_ha",
            "efficiency_pct", "total_area", "season"
        ]].rename(columns={
            "crop_category_x": "crop_category",
            "benchmark": "avg_yield_benchmark_ton_per_ha",
            "total_area": "total_area_planted_ha",
        }).to_dict(orient="records")

        return {
            "filters_applied": filters_applied,
            "data": data
        }

    except Exception as e:
        logger.error(f"get_yield_efficiency failed: {e}")
        raise DatabaseError(str(e))
def get_seasonal_trend(crop_name=None, crop_category=None, year=None, quarter=None, market_type=None):
    try:
        df = fetch_data("SELECT * FROM vw_harvest_full")

        if crop_name:
            df = df[df["crop_name"] == crop_name]
        if crop_category:
            df = df[df["crop_category"] == crop_category]
        if year:
            df = df[df["year"] == year]
        if quarter:
            df = df[df["quarter"] == quarter]
        if market_type:
            df = df[df["market_type"] == market_type]

        grouped = df.groupby(["crop_name", "year", "quarter", "season"]).agg(
            total_quantity_sold_ton=("quantity_sold_ton", "sum"),
            total_revenue_bdt=("revenue_bdt", "sum"),
            avg_price_per_ton_bdt=("price_per_ton_bdt", "mean"),
            num_harvests=("harvest_id", "count"),
        ).reset_index()

        grouped["avg_price_per_ton_bdt"] = grouped["avg_price_per_ton_bdt"].round(0)

        filters_applied = {}
        if crop_name:
            filters_applied["crop_name"] = crop_name
        if crop_category:
            filters_applied["crop_category"] = crop_category
        if year:
            filters_applied["year"] = year
        if quarter:
            filters_applied["quarter"] = quarter
        if market_type:
            filters_applied["market_type"] = market_type

        return {
            "filters_applied": filters_applied,
            "trend": grouped[[
                "crop_name", "year", "quarter", "season",
                "total_quantity_sold_ton", "total_revenue_bdt",
                "avg_price_per_ton_bdt", "num_harvests"
            ]].to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"get_seasonal_trend failed: {e}")
        raise DatabaseError(str(e))


def get_quality_breakdown(crop_id=None, crop_category=None, year=None, region=None, market_type=None, pesticide_residue=None):
    try:
        df = fetch_data("SELECT * FROM vw_harvest_full")
        if crop_id:
            crop_df = fetch_data(f"SELECT crop_name FROM dim_crop WHERE crop_id = {crop_id}")
            if not crop_df.empty:
                crop_name = crop_df.iloc[0]["crop_name"]
                df = df[df["crop_name"] == crop_name]

        if crop_category:
            df = df[df["crop_category"] == crop_category]
        if year:
            df = df[df["year"] == year]
        if region:
            df = df[df["region"] == region]
        if market_type:
            df = df[df["market_type"] == market_type]
        if pesticide_residue:
            df = df[df["pesticide_residue"] == pesticide_residue]

        total_records = len(df)

        grade_dist = {}
        for grade in ["A", "B", "C", "D"]:
            grade_df = df[df["quality_grade"] == grade]
            count = len(grade_df)
            grade_dist[grade] = {
                "count": count,
                "pct": round((count / total_records * 100), 1) if total_records > 0 else 0,
                "avg_revenue_bdt": round(grade_df["revenue_bdt"].mean(), 0) if count > 0 else 0
            }

        residue_dist = {}
        for residue in ["None", "Trace", "Low", "High"]:
            residue_df = df[df["pesticide_residue"] == residue]
            count = len(residue_df)
            residue_dist[residue] = {
                "count": count,
                "pct": round((count / total_records * 100), 1) if total_records > 0 else 0
            }

        filters_applied = {}
        if crop_id:
            filters_applied["crop_id"] = crop_id
        if crop_category:
            filters_applied["crop_category"] = crop_category
        if year:
            filters_applied["year"] = year
        if region:
            filters_applied["region"] = region
        if market_type:
            filters_applied["market_type"] = market_type
        if pesticide_residue:
            filters_applied["pesticide_residue"] = pesticide_residue

        return {
            "filters_applied": filters_applied,
            "total_records": total_records,
            "grade_distribution": grade_dist,
            "pesticide_residue_breakdown": residue_dist
        }

    except Exception as e:
        logger.error(f"get_quality_breakdown failed: {e}")
        raise DatabaseError(str(e))