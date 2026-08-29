from decimal import Decimal
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ScrapedProduct(BaseModel):
    name: str = Field(..., min_length=1)
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="GBP", max_length=3)
    category: Optional[str] = "Books"
    source: str = "BooksToScrape"
    product_url: HttpUrl
    image_url: Optional[HttpUrl] = None
    in_stock: bool = True