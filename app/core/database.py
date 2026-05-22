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

def fetch_data(query: str, params: dict = None) -> pd.DataFrame:
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine, params=params)
        logger.info(f"Query executed successfully, rows returned: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
    
    
def _extract_active_filters(**kwargs) -> dict[str, any]:
    """Helper function to remove None values and extract applied filters dynamically."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _build_sql_query(base_view: str, filters: dict[str, any]) -> tuple:
    if not filters:
        return f"SELECT * FROM {base_view}", {}
    
    conditions = []
    params = {}
    for key, value in filters.items():
        conditions.append(f"{key} = %({key})s")
        params[key] = value
        
    query = f"SELECT * FROM {base_view} WHERE {' AND '.join(conditions)}"
    return query, params


if __name__ == "__main__":
    df = fetch_data("SELECT DISTINCT farm_district FROM vw_harvest_full ORDER BY farm_district")
    print(df["farm_district"].tolist())