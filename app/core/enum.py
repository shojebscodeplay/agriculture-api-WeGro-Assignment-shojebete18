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


class DistrictEnum(str, Enum):
    BAGERHAT = "Bagerhat"
    BARISAL = "Barisal"
    BHOLA = "Bhola"
    CHAPAINAWABGANJ = "Chapainawabganj"
    COMILLA = "Comilla"
    FENI = "Feni"
    GAZIPUR = "Gazipur"
    GOPALGANJ = "Gopalganj"
    JAMALPUR = "Jamalpur"
    JASHORE = "Jashore"
    KISHOREGANJ = "Kishoreganj"
    KURIGRAM = "Kurigram"
    LALMONIRHAT = "Lalmonirhat"
    MANIKGANJ = "Manikganj"
    MOULVIBAZAR = "Moulvibazar"
    MYMENSINGH = "Mymensingh"
    NARSINGDI = "Narsingdi"
    NOAKHALI = "Noakhali"
    PABNA = "Pabna"
    PATUAKHALI = "Patuakhali"
    RAJSHAHI = "Rajshahi"
    RANGAMATI = "Rangamati"
    RANGPUR = "Rangpur"
    SATKHIRA = "Satkhira"
    SIRAJGANJ = "Sirajganj"
    SUNAMGANJ = "Sunamganj"
    SYLHET = "Sylhet"
    TANGAIL = "Tangail"

class WaterRequiredEnum(str, Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"
    
from enum import Enum


class CropNameEnum(str, Enum):
    AMAN_RICE = "Aman Rice"
    BORO_RICE = "Boro Rice"
    AUS_RICE = "Aus Rice"

    WHEAT = "Wheat"
    MAIZE = "Maize"

    POTATO = "Potato"
    TOMATO = "Tomato"
    ONION = "Onion"
    GARLIC = "Garlic"
    BRINJAL = "Brinjal"

    MUSTARD = "Mustard"
    SOYBEAN = "Soybean"
    LENTIL = "Lentil"

    JUTE = "Jute"
    SUGARCANE = "Sugarcane"

    MANGO = "Mango"
    BANANA = "Banana"
    JACKFRUIT = "Jackfruit"

    TURMERIC = "Turmeric"
    CHILLI = "Chilli"
    
class PesticideResidue(str, Enum):
    NONE = "None"
    TRACE = "Trace"
    LOW = "Low"