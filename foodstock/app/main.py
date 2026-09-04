from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.models import FoodItem


app = FastAPI(
    title="FoodStock API",
    description="Private API für die selbst gehostete FoodStock-App",
    version="0.2.0",
)


class FoodItemCreate(BaseModel):
    name: str
    quantity: int = 1
    unit: str = "Stück"
    category: str | None = None
    expires_at: date | None = None


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "application": "FoodStock",
        "status": "ok",
        "version": "0.2.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/database-configured")
def database_configured():
    return {
        "database": engine.url.database,
        "driver": engine.url.drivername,
        "host": engine.url.host,
        "port": engine.url.port,
    }


@app.get("/db-health")
def db_health():
    try:
        with engine.connect() as connection:
            value = connection.execute(text("SELECT 1")).scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "test": value,
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "connection_failed",
            "error": str(error),
        }


@app.get("/items")
def get_items():
    with SessionLocal() as session:
        items = session.query(FoodItem).order_by(FoodItem.id).all()

        return [
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "expires_at": item.expires_at,
            }
            for item in items
        ]


@app.post("/items")
def create_item(item_data: FoodItemCreate):
    with SessionLocal() as session:
        item = FoodItem(
            name=item_data.name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            category=item_data.category,
            expires_at=item_data.expires_at,
        )

        session.add(item)
        session.commit()
        session.refresh(item)

        return {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "category": item.category,
            "expires_at": item.expires_at,
        }


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with SessionLocal() as session:
        item = session.get(FoodItem, item_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Lebensmittel nicht gefunden",
            )

        session.delete(item)
        session.commit()

        return {
            "status": "deleted",
            "id": item_id,
        }
