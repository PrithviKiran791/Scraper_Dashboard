from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PriceHistory, Product, ScrapingRun
from ..schemas import StatisticsResponse

router = APIRouter(
    prefix="/api",
    tags=["Analytics"],
)


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
)
def get_statistics(
    db: Session = Depends(get_db),
):
    total_products = db.scalar(
        select(func.count(Product.id))
    ) or 0

    latest_prices = (
        select(
            PriceHistory.product_id,
            func.max(PriceHistory.scraped_at).label("latest_time"),
        )
        .group_by(PriceHistory.product_id)
        .subquery()
    )

    latest_price_values = (
        select(PriceHistory.price)
        .join(
            latest_prices,
            (PriceHistory.product_id == latest_prices.c.product_id)
            & (PriceHistory.scraped_at == latest_prices.c.latest_time),
        )
    )

    average_price = db.scalar(
        select(func.avg(latest_price_values.c.price))
    )

    price_drops = 0

    products = db.scalars(select(Product)).all()

    for product in products:
        prices = db.scalars(
            select(PriceHistory)
            .where(PriceHistory.product_id == product.id)
            .order_by(PriceHistory.scraped_at.desc())
            .limit(2)
        ).all()

        if len(prices) == 2 and prices[0].price < prices[1].price:
            price_drops += 1

    latest_scrape = db.scalar(
        select(ScrapingRun.completed_at)
        .where(ScrapingRun.completed_at.is_not(None))
        .order_by(ScrapingRun.completed_at.desc())
    )

    return StatisticsResponse(
        total_products=total_products,
        average_price=(
            float(average_price)
            if average_price is not None
            else None
        ),
        price_drops=price_drops,
        latest_scrape=latest_scrape,
    ) 