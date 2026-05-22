import logging
import pandas as pd
from app.core.database import fetch_data, _extract_active_filters, _build_sql_query
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def get_yield_efficiency(region=None, crop_category=None, year=None, season=None, water_requirement=None):
    try:
        filters_applied = _extract_active_filters(
            region=region, crop_category=crop_category, 
            year=year, season=season, water_requirement=water_requirement
        )

        sql_filters = filters_applied.copy()
        if "crop_category" in sql_filters:
            sql_filters["crop_category"] = sql_filters.pop("crop_category")

        harvest_query, harvest_params = _build_sql_query("vw_harvest_full", {k: v for k, v in sql_filters.items() if k != "water_requirement"})
        df = fetch_data(harvest_query, harvest_params)
        
        crop_query, crop_params = _build_sql_query("dim_crop", {"water_requirement": water_requirement} if water_requirement else {})
        crop_dim = fetch_data(crop_query, crop_params)

        if df.empty or crop_dim.empty:
            return {"filters_applied": filters_applied, "data": []}

        df = df.merge(crop_dim, on="crop_name", how="inner" if water_requirement else "left")
        
        if df.empty:
            return {"filters_applied": filters_applied, "data": []}

        category_col = "crop_category_x" if "crop_category_x" in df.columns else "crop_category"

        grouped = df.groupby(["crop_name", category_col]).agg(
            total_harvested=("quantity_harvested_ton", "sum"),
            total_area=("area_planted_ha", "sum"),
            benchmark=("avg_yield_ton_per_ha", "first"),
            season_val=("season", "first"),
        ).reset_index()

        grouped["actual_avg_yield_ton_per_ha"] = round(grouped["total_harvested"] / grouped["total_area"], 2)
        grouped["efficiency_pct"] = round((grouped["actual_avg_yield_ton_per_ha"] / grouped["benchmark"]) * 100, 1)

        data = grouped[[
            "crop_name", category_col,
            "benchmark", "actual_avg_yield_ton_per_ha",
            "efficiency_pct", "total_area", "season_val"
        ]].rename(columns={
            category_col: "crop_category",
            "benchmark": "avg_yield_benchmark_ton_per_ha",
            "total_area": "total_area_planted_ha",
            "season_val": "season"
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
        filters_applied = _extract_active_filters(
            crop_name=crop_name, crop_category=crop_category, 
            year=year, quarter=quarter, market_type=market_type
        )
        
        query, params = _build_sql_query("vw_harvest_full", filters_applied)
        df = fetch_data(query, params)


        if df.empty:
            return {"filters_applied": filters_applied, "trend": []}

        grouped = df.groupby(["crop_name", "year", "quarter", "season"]).agg(
            total_quantity_sold_ton=("quantity_sold_ton", "sum"),
            total_revenue_bdt=("revenue_bdt", "sum"),
            avg_price_per_ton_bdt=("price_per_ton_bdt", "mean"),
            num_harvests=("harvest_id", "count"),
        ).reset_index()

        grouped["avg_price_per_ton_bdt"] = grouped["avg_price_per_ton_bdt"].round(0)

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
        filters_applied = _extract_active_filters(
            crop_id=crop_id, crop_category=crop_category, year=year, 
            region=region, market_type=market_type, pesticide_residue=pesticide_residue
        )

        sql_filters = {k: v for k, v in filters_applied.items() if k not in ["crop_id", "pesticide_residue"]}
        
        if crop_id:
            crop_df = fetch_data(f"SELECT crop_name FROM dim_crop WHERE crop_id = {crop_id}")
            if not crop_df.empty:
                sql_filters["crop_name"] = crop_df.iloc[0]["crop_name"]
        
        if pesticide_residue:
            sql_filters["pesticide_residue"] = pesticide_residue

        query, params = _build_sql_query("vw_harvest_full", sql_filters)
        df = fetch_data(query, params)

        total_records = len(df)

        grade_dist = {}
        if total_records > 0:
            for grade in ["A", "B", "C", "D"]:
                grade_df = df[df["quality_grade"] == grade]
                count = len(grade_df)
                grade_dist[grade] = {
                    "count": count,
                    "pct": round((count / total_records * 100), 1),
                    "avg_revenue_bdt": round(grade_df["revenue_bdt"].mean(), 0) if count > 0 else 0
                }
        else:
            grade_dist = {g: {"count": 0, "pct": 0, "avg_revenue_bdt": 0} for g in ["A", "B", "C", "D"]}

        residue_dist = {}
        if total_records > 0:
            for residue in ["None", "Trace", "Low", "High"]:
                count = len(df[df["pesticide_residue"] == residue])
                residue_dist[residue] = {
                    "count": count,
                    "pct": round((count / total_records * 100), 1)
                }
        else:
            residue_dist = {r: {"count": 0, "pct": 0} for r in ["None", "Trace", "Low", "High"]}

        return {
            "filters_applied": filters_applied,
            "total_records": total_records,
            "grade_distribution": grade_dist,
            "pesticide_residue_breakdown": residue_dist
        }

    except Exception as e:
        logger.error(f"get_quality_breakdown failed: {e}")
        raise DatabaseError(str(e))