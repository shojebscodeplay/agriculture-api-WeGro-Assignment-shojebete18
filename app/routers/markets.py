import logging
from fastapi import APIRouter, Query
from app.services.market_service import get_price_comparison
from app.core.enum import MarketTypeEnum, CropCategoryEnum, SeasonEnum, YearEnum, Price_tierEnum, DistrictEnum

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets", tags=["Markets"])


@router.get("/price-comparison")
def price_comparison(
    market_type: MarketTypeEnum = Query(None, description="Filter by market type"),
    crop_category: CropCategoryEnum = Query(None, description="Filter by crop category"),
    year: YearEnum = Query(None, description="Filter by year"),
    season: SeasonEnum = Query(None, description="Filter by season"),
    price_tier: Price_tierEnum = Query(None, description="Filter by price tier"),
    district: DistrictEnum = Query(None, description="Filter by district"),
):
    return get_price_comparison(
        market_type=market_type.value if market_type else None,
        crop_category=crop_category.value if crop_category else None,
        year=year.value if year else None,
        season=season.value if season else None,
        price_tier=price_tier.value if price_tier else None,
        district=district.value if district else None,
    )