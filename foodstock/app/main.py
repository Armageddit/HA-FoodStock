from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine


app = FastAPI(
    title="FoodStock API",
    description="Private API für die selbst gehostete FoodStock-App",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "application": "FoodStock",
        "status": "ok",
        "version": "0.1.0",
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
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

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
