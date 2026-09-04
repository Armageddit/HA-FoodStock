from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Stück",
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    expires_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
