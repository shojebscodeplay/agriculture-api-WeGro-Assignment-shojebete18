import os
import logging
from typing import Any
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

ALLOWED_VIEWS = {"vw_harvest_full"}

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine
    try:
        url = (
            f"mysql+pymysql://{os.getenv('USER')}:{os.getenv('PASSWORD')}"
            f"@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DB')}"
        )
        _engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        logger.info("Database engine created successfully")
        return _engine
    except Exception:
        logger.error("Database engine creation failed", exc_info=True)
        raise


def fetch_data(query: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
        logger.info("Query executed successfully, rows returned: %d", len(df))
        return df
    except Exception:
        logger.error("Query execution failed", exc_info=True)
        raise


def _extract_active_filters(**kwargs) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _build_sql_query(base_view: str, filters: dict[str, Any]) -> tuple[str, dict]:
    if base_view not in ALLOWED_VIEWS:
        raise ValueError(f"Unauthorized view: {base_view}")
    if not filters:
        return f"SELECT * FROM {base_view}", {}
    conditions = [f"{k} = :{k}" for k in filters]  # SQLAlchemy :param style
    query = f"SELECT * FROM {base_view} WHERE {' AND '.join(conditions)}"
    return query, filters