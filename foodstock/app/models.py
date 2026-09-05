"""Relational persistence model for the FoodStock API.

The database is deliberately the source of truth.  The mobile client only sends
commands (for example ``consume``), never a calculated new stock value.
"""
from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class InventoryStatus(str, Enum):
    ACTIVE = "active"
    CONSUMED = "consumed"
    MISSING = "missing"  # a confirmed shortfall; makes a negative stock possible
    DELETED = "deleted"


class ShoppingStatus(str, Enum):
    NEEDED = "needed"
    ON_LIST = "on_list"
    PURCHASED = "purchased"
    STOCKED = "stocked"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.USER)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StorageLocation(Base):
    __tablename__ = "storage_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("storage_locations.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    barcode: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(120))
    unit: Mapped[str] = mapped_column(String(50), default="Stück")
    image_path: Mapped[str | None] = mapped_column(String(500))
    default_storage_location_id: Mapped[int | None] = mapped_column(ForeignKey("storage_locations.id"))
    minimum_stock: Mapped[int] = mapped_column(Integer, default=0)
    ideal_stock: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Inventory(Base):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    expiration_date: Mapped[date | None] = mapped_column(Date, index=True)
    storage_location_id: Mapped[int | None] = mapped_column(ForeignKey("storage_locations.id"))
    status: Mapped[InventoryStatus] = mapped_column(SqlEnum(InventoryStatus), default=InventoryStatus.ACTIVE, index=True)
    image_path: Mapped[str | None] = mapped_column(String(500))
    added_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ShoppingListItem(Base):
    __tablename__ = "shopping_list"
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ShoppingStatus] = mapped_column(SqlEnum(ShoppingStatus), default=ShoppingStatus.NEEDED)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("client_operation_id", name="uq_transaction_operation"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    inventory_id: Mapped[int | None] = mapped_column(ForeignKey("inventory.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event: Mapped[str] = mapped_column(String(30))
    quantity_delta: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text)
    client_operation_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
