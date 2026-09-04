from fastapi import FastAPI

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
