import logging
from fastapi import APIRouter, Query
from app.services.crop_service import get_yield_efficiency, get_seasonal_trend, get_quality_breakdown
from app.core.enum import RegionEnum, CropCategoryEnum, SeasonEnum, YearEnum, MarketTypeEnum

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.get("/yield-efficiency")
def yield_efficiency(
    region: RegionEnum = Query(None, description="Filter by region"),
    crop_category: CropCategoryEnum = Query(None, description="Filter by crop category"),
    year: YearEnum = Query(None, description="Filter by year"),
    season: SeasonEnum = Query(None, description="Filter by season"),
    water_requirement: str = Query(None, description="Filter by water requirement"),
):
    return get_yield_efficiency(
        region=region.value if region else None,
        crop_category=crop_category.value if crop_category else None,
        year=year.value if year else None,
        season=season.value if season else None,
        water_requirement=water_requirement,
    )


@router.get("/seasonal-trend")
def seasonal_trend(
    crop_name: str = Query(None, description="Filter by crop name"),
    crop_category: CropCategoryEnum = Query(None, description="Filter by crop category"),
    year: YearEnum = Query(None, description="Filter by year"),
    quarter: int = Query(None, description="Filter by quarter (1-4)"),
    market_type: MarketTypeEnum = Query(None, description="Filter by market type"),
):
    return get_seasonal_trend(
        crop_name=crop_name,
        crop_category=crop_category.value if crop_category else None,
        year=year.value if year else None,
        quarter=quarter,
        market_type=market_type.value if market_type else None,
    )


@router.get("/quality-breakdown")
def quality_breakdown(
    crop_id: int = Query(None, description="Filter by crop ID"),
    crop_category: CropCategoryEnum = Query(None, description="Filter by crop category"),
    year: YearEnum = Query(None, description="Filter by year"),
    region: RegionEnum = Query(None, description="Filter by region"),
    market_type: MarketTypeEnum = Query(None, description="Filter by market type"),
    pesticide_residue: str = Query(None, description="Filter by pesticide residue"),
):
    return get_quality_breakdown(
        crop_id=crop_id,
        crop_category=crop_category.value if crop_category else None,
        year=year.value if year else None,
        region=region.value if region else None,
        market_type=market_type.value if market_type else None,
        pesticide_residue=pesticide_residue,
    )