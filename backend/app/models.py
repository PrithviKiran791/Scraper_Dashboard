from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    product_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    in_stock: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    price_history: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="price_history",
    )


class ScrapingRun(Base):
    __tablename__ = "scraping_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    products_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )