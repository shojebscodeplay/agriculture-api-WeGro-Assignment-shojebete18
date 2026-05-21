import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_engine():
    try:
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
        db = os.getenv("DB")

        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
        )
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def fetch_data(query: str) -> pd.DataFrame:
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine)
        logger.info(f"Query executed successfully, rows returned: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
    
if __name__ == "__main__":
    df = fetch_data("SELECT * FROM vw_harvest_full")
    crop_dim = fetch_data("SELECT * FROM dim_crop")
    df = df.merge(crop_dim, on="crop_name", how="left")
    
    grouped = df.groupby(["crop_name", "crop_category_x"]).agg(
        total_harvested=("quantity_harvested_ton", "sum"),
        total_area=("area_planted_ha", "sum"),
        benchmark=("avg_yield_ton_per_ha", "first"),
    ).reset_index()
    
    grouped["actual"] = round(grouped["total_harvested"] / grouped["total_area"], 2)
    grouped["efficiency"] = round((grouped["actual"] / grouped["benchmark"]) * 100, 1)
    
    print(grouped[["crop_name", "total_harvested", "total_area", "actual", "benchmark", "efficiency"]])