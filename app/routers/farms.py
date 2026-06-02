import logging
from fastapi import APIRouter, Query
from app.services.farm_service import get_farm_summary, get_farm_performance, get_top_farms , get_loss_analysis
from app.core.enum import RegionEnum, FarmTypeEnum, YearEnum, CropCategoryEnum, MarketTypeEnum, MetricEnum,SeasonEnum, QualityGradeEnum

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/farms", tags=["Farms"])

@router.get("/summary")
def farm_summary(
    region: RegionEnum = Query(None, description="Filter by region"),
    farm_type: FarmTypeEnum = Query(None, description="Filter by farm type"),
    year: YearEnum = Query(None, description="Filter by year"),
    season: SeasonEnum = Query(None, description="Filter by season"),
):
    return get_farm_summary(
        region=region.value if region else None,
        farm_type=farm_type.value if farm_type else None,
        year=year.value if year else None,
        season=season.value if season else None,
    )

@router.get("/{farm_id}/performance")
def farm_performance(
    farm_id: int,
    year: YearEnum = Query(None, description="Filter by year"),
    crop_category: CropCategoryEnum = Query(None, description="Filter by crop category"),
    market_type: MarketTypeEnum = Query(None, description="Filter by market type"),
):
    return get_farm_performance(
        farm_id=farm_id,
        year=year.value if year else None,
        crop_category=crop_category.value if crop_category else None,
        market_type=market_type.value if market_type else None,
    )

@router.get("/top")
def top_farms(
    metric: MetricEnum = Query(MetricEnum.profit, description="Rank by metric"),
    region: RegionEnum = Query(None, description="Filter by region"),
    farm_type: FarmTypeEnum = Query(None, description="Filter by farm type"),
    year: YearEnum = Query(None, description="Filter by year"),
    limit: int = Query(10, description="Number of results"),
):
    return get_top_farms(
        metric=metric.value,
        region=region.value if region else None,
        farm_type=farm_type.value if farm_type else None,
        year=year.value if year else None,
        limit=limit,
    )
    
@router.get("/loss_analysis")
def loss_analysis( 
    year: YearEnum = Query(None, description="Filter by year"),
    region: RegionEnum = Query(None, description="Filter by region"),
    crop_category: CropCategoryEnum = Query(None, description="Filter by crop category"),
    season : SeasonEnum = Query(None, description="Filter by crop season"),
    quality_grade : QualityGradeEnum = Query(None, description="Filter by quality grade")
):
    return get_loss_analysis(
        year=year.value if year else None,
        region=region.value if region else None,
        crop_category=( crop_category.value if crop_category else None),
        season=season.value if season else None,
        quality_grade=(quality_grade.value if quality_grade else None)
    )