from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .models import PriceHistory, Product, ScrapingRun
from .routes.analytics import router as analytics_router
from .routes.products import router as products_router
from .routes.scraping_runs import router as scraping_runs_router 

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scraper Dashboard API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(analytics_router) 
app.include_router(scraping_runs_router) 


@app.get("/")
def root():
    return {
        "message": "Scraper Dashboard API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }