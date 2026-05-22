from enum import Enum

class RegionEnum(str, Enum):
    dhaka = "Dhaka"
    chittagong = "Chittagong"
    sylhet = "Sylhet"
    rajshahi = "Rajshahi"
    khulna = "Khulna"
    rangpur = "Rangpur"
    barisal = "Barisal"
    mymensingh = "Mymensingh"

class FarmTypeEnum(str, Enum):
    small = "Small"
    medium = "Medium"
    large = "Large"
    commercial = "Commercial"

class SeasonEnum(str, Enum):
    spring = "Spring"
    summer = "Summer"
    autumn = "Autumn"
    winter = "Winter"

class YearEnum(int, Enum):
    y2022 = 2022
    y2023 = 2023
    y2024 = 2024

class CropCategoryEnum(str, Enum):
    cereal = "Cereal"
    vegetable = "Vegetable"
    fruit = "Fruit"
    pulse = "Pulse"
    oilseed = "Oilseed"
    cash_crop = "Cash Crop"
    spice = "Spice"

class MarketTypeEnum(str, Enum):
    local = "Local"
    wholesale = "Wholesale"
    export = "Export"
    retail = "Retail"
    government = "Government Procurement"

class MetricEnum(str, Enum):
    profit = "profit"
    revenue = "revenue"
    yield_ = "yield"

class QualityGradeEnum(str, Enum):
    a = "A"
    b = "B"
    c = "C"
    d = "D"
    
class Price_tierEnum(str,Enum):
    Low = "Low",
    Medium = "Medium", 
    High = "High",
    Premium = "Premium" 