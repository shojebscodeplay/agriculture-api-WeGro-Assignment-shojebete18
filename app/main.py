import logging
from fastapi import FastAPI
from app.core.exceptions import global_exception_handler
from app.routers.farms import router as farms_router
from app.routers.crops import router as crops_router
from app.routers.markets import router as markets_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Agriculture API",
    description="Agriculture Database Analytics API",
    version="1.0.0"
)

# Handles unexpected exceptions
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(farms_router)
app.include_router(crops_router)
app.include_router(markets_router)


@app.get("/")
async def health_check():
    return {"status": "ok"}