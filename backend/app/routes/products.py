from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PriceHistory, Product
from ..schemas import (
    PriceHistoryResponse,
    ProductCreate,
    ProductHistoryResponse,
    ProductListResponse,
    ProductResponse,
)

router = APIRouter(
    prefix="/api/products",
    tags=["Products"],
)


def get_product_prices(
    db: Session,
    product_id: int,
):
    prices = db.scalars(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(desc(PriceHistory.scraped_at))
    ).all()

    current_price = None
    previous_price = None

    if len(prices) >= 1:
        current_price = float(prices[0].price)

    if len(prices) >= 2:
        previous_price = float(prices[1].price)

    price_change = None
    price_change_percentage = None

    if current_price is not None and previous_price is not None:
        price_change = current_price - previous_price

        if previous_price != 0:
            price_change_percentage = (
                (current_price - previous_price)
                / previous_price
            ) * 100

    return (
        current_price,
        previous_price,
        price_change,
        price_change_percentage,
    )


@router.post("", response_model=ProductResponse)
def create_or_update_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    product = db.scalar(
        select(Product).where(
            Product.product_url == product_data.product_url
        )
    )

    if product is None:
        product = Product(
            name=product_data.name,
            category=product_data.category,
            source=product_data.source,
            product_url=product_data.product_url,
            image_url=product_data.image_url,
            currency=product_data.currency,
            in_stock=product_data.in_stock,
        )

        db.add(product)
        db.flush()

    else:
        product.name = product_data.name
        product.category = product_data.category
        product.source = product_data.source
        product.image_url = product_data.image_url
        product.currency = product_data.currency
        product.in_stock = product_data.in_stock

    price_history = PriceHistory(
        product_id=product.id,
        price=product_data.price,
    )

    db.add(price_history)

    db.commit()
    db.refresh(product)

    (
        current_price,
        previous_price,
        price_change,
        price_change_percentage,
    ) = get_product_prices(db, product.id)

    return ProductResponse(
        id=product.id,
        name=product.name,
        price=current_price,
        currency=product.currency,
        category=product.category,
        source=product.source,
        product_url=product.product_url,
        image_url=product.image_url,
        in_stock=product.in_stock,
        previous_price=previous_price,
        price_change=price_change,
        price_change_percentage=price_change_percentage,
    )


@router.get("", response_model=ProductListResponse)
def get_products(
    db: Session = Depends(get_db),
):
    products = db.scalars(
        select(Product).order_by(Product.id)
    ).all()

    result = []

    for product in products:
        (
            current_price,
            previous_price,
            price_change,
            price_change_percentage,
        ) = get_product_prices(db, product.id)

        result.append(
            ProductResponse(
                id=product.id,
                name=product.name,
                price=current_price,
                currency=product.currency,
                category=product.category,
                source=product.source,
                product_url=product.product_url,
                image_url=product.image_url,
                in_stock=product.in_stock,
                previous_price=previous_price,
                price_change=price_change,
                price_change_percentage=price_change_percentage,
            )
        )

    return ProductListResponse(products=result)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    (
        current_price,
        previous_price,
        price_change,
        price_change_percentage,
    ) = get_product_prices(db, product.id)

    return ProductResponse(
        id=product.id,
        name=product.name,
        price=current_price,
        currency=product.currency,
        category=product.category,
        source=product.source,
        product_url=product.product_url,
        image_url=product.image_url,
        in_stock=product.in_stock,
        previous_price=previous_price,
        price_change=price_change,
        price_change_percentage=price_change_percentage,
    )


@router.get(
    "/{product_id}/history",
    response_model=ProductHistoryResponse,
)
def get_product_history(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    history = db.scalars(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at)
    ).all()

    return ProductHistoryResponse(
        product_id=product_id,
        history=[
            PriceHistoryResponse.model_validate(item)
            for item in history
        ],
    )