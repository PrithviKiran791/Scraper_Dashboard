from decimal import Decimal
from typing import Optional

from pydantic import Field, HttpUrl

from app.models.base import ScrapedRecord


class ScrapedProduct(ScrapedRecord):
    name: str = Field(..., min_length=1)
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="GBP", max_length=3)
    category: Optional[str] = "Books"
    product_url: HttpUrl
    image_url: Optional[HttpUrl] = None
    in_stock: bool = True