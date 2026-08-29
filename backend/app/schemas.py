from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    price: float
    currency: str
    category: str | None = None
    source: str
    product_url: str
    image_url: str | None = None
    in_stock: bool = True


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float | None = None
    currency: str
    category: str | None = None
    source: str
    product_url: str
    image_url: str | None = None
    in_stock: bool = True
    previous_price: float | None = None
    price_change: float | None = None
    price_change_percentage: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    products: list[ProductResponse]


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductHistoryResponse(BaseModel):
    product_id: int
    history: list[PriceHistoryResponse]


class StatisticsResponse(BaseModel):
    total_products: int
    average_price: float | None
    price_drops: int
    latest_scrape: datetime | None