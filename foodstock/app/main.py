from datetime import date, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text

from app.database import SessionLocal, engine
from app.models import FoodItem


app = FastAPI(
    title="FoodStock API",
    description="Private API für die selbst gehostete FoodStock-App",
    version="0.2.1",
)


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=0)
    unit: str = Field(default="Stück", min_length=1, max_length=50)
    category: str | None = Field(default=None, max_length=100)
    expiry_date: date | None = None


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    category: str | None = Field(default=None, max_length=100)
    expiry_date: date | None = None


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    quantity: int
    unit: str
    category: str | None
    expiry_date: date | None
    created_at: datetime
    updated_at: datetime


@app.on_event("startup")
def startup():
    FoodItem.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "application": "FoodStock",
        "status": "ok",
        "version": "0.2.1",
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "test": result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Datenbank nicht erreichbar: {exc}",
        )


@app.get("/database-configured")
def database_configured():
    return {
        "database": engine.url.database,
        "driver": engine.url.drivername,
        "host": engine.url.host,
        "port": engine.url.port,
    }


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    with SessionLocal() as session:
        food_item = FoodItem(**item.model_dump())

        session.add(food_item)
        session.commit()
        session.refresh(food_item)

        return food_item


@app.get("/items", response_model=list[ItemResponse])
def get_items():
    with SessionLocal() as session:
        statement = select(FoodItem).order_by(FoodItem.id)
        return list(session.scalars(statement).all())


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    with SessionLocal() as session:
        food_item = session.get(FoodItem, item_id)

        if food_item is None:
            raise HTTPException(
                status_code=404,
                detail="Artikel nicht gefunden",
            )

        return food_item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate):
    with SessionLocal() as session:
        food_item = session.get(FoodItem, item_id)

        if food_item is None:
            raise HTTPException(
                status_code=404,
                detail="Artikel nicht gefunden",
            )

        update_data = item.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(food_item, field, value)

        session.commit()
        session.refresh(food_item)

        return food_item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with SessionLocal() as session:
        food_item = session.get(FoodItem, item_id)

        if food_item is None:
            raise HTTPException(
                status_code=404,
                detail="Artikel nicht gefunden",
            )

        session.delete(food_item)
        session.commit()

        return {
            "status": "deleted",
            "id": item_id,
        }
