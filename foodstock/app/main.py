"""FoodStock's authenticated REST API.

It is intentionally a small, self-contained FastAPI service suited to a Home
Assistant add-on.  All changes go through transactional server-side commands,
which also makes offline replay idempotent.
"""
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import (Inventory, InventoryStatus, Product, ShoppingListItem,
                        ShoppingStatus, StorageLocation, Transaction, User, UserRole)

API_VERSION = "1.0.0"
DATA_DIR = Path(os.getenv("FOODSTOCK_DATA_DIR", "/data/foodstock"))
JWT_SECRET = os.getenv("JWT_SECRET", "")
DEFAULT_JWT_SECRET = "CHANGE-ME-use-a-random-secret-with-at-least-32-characters"
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "168"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI(title="FoodStock API", version=API_VERSION, description="Private authenticated FoodStock API")
app.mount("/ui", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="ui")

def db_session():
    db = SessionLocal()
    try: yield db
    finally: db.close()
DB = Annotated[Session, Depends(db_session)]

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)
    role: UserRole = UserRole.USER
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; username: str; role: UserRole; active: bool; created_at: datetime
class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=12, max_length=128)
    role: UserRole | None = None
    active: bool | None = None
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class LocationIn(BaseModel): name: str = Field(min_length=1, max_length=120); parent_id: int | None = None
class LocationOut(LocationIn):
    model_config = ConfigDict(from_attributes=True)
    id: int; active: bool
class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    parent_id: int | None = None
    active: bool | None = None
class ProductIn(BaseModel):
    barcode: str | None = Field(default=None, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=120)
    unit: str = Field(default="Stück", min_length=1, max_length=50)
    default_storage_location_id: int | None = None
    minimum_stock: int = Field(default=0, ge=0)
    ideal_stock: int | None = Field(default=None, ge=0)
class ProductUpdate(ProductIn): active: bool | None = None
class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    id: int; image_path: str | None; active: bool; created_at: datetime; updated_at: datetime
    stock: int = 0
class InventoryIn(BaseModel):
    product_id: int; quantity: int = Field(default=1, ge=1, le=1000)
    expiration_date: date | None = None; storage_location_id: int | None = None
    save_expiration_image: bool = False; client_operation_id: UUID | None = None
class ConsumeIn(BaseModel):
    quantity: int = Field(default=1, ge=1, le=1000); reason: str | None = Field(default="verbraucht", max_length=1000)
    client_operation_id: UUID | None = None
class CorrectIn(BaseModel):
    quantity_delta: int = Field(ge=-1000, le=1000); reason: str = Field(min_length=3, max_length=1000)
    client_operation_id: UUID | None = None
class ShoppingUpdate(BaseModel): status: ShoppingStatus

def current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DB) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Ungültiges oder abgelaufenes Token", headers={"WWW-Authenticate": "Bearer"})
    user = db.get(User, user_id)
    if not user or not user.active: raise HTTPException(401, "Benutzer ist nicht aktiv")
    return user
CurrentUser = Annotated[User, Depends(current_user)]
def admin(user: CurrentUser) -> User:
    if user.role != UserRole.ADMIN: raise HTTPException(403, "Administratorrechte erforderlich")
    return user
Admin = Annotated[User, Depends(admin)]

def ensure_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Produkt nicht gefunden")
    return product
def stock_query(product_id: int):
    return select(func.coalesce(func.sum(case((Inventory.status == InventoryStatus.ACTIVE, Inventory.quantity), (Inventory.status == InventoryStatus.MISSING, -Inventory.quantity), else_=0)), 0)).where(Inventory.product_id == product_id)
def stock(db: Session, product_id: int) -> int: return int(db.scalar(stock_query(product_id)) or 0)
def product_out(db: Session, product: Product) -> ProductOut:
    """Build the public product representation with its derived stock."""
    data = {column.name: getattr(product, column.name) for column in Product.__table__.columns}
    data["stock"] = stock(db, product.id)
    return ProductOut(**data)
def update_shopping(db: Session, product: Product, actor_id: int):
    amount = stock(db, product.id)
    required = (product.ideal_stock if product.ideal_stock is not None else product.minimum_stock) - amount
    item = db.get(ShoppingListItem, product.id)
    if amount < product.minimum_stock:
        if not item: item = ShoppingListItem(product_id=product.id); db.add(item)
        if item.status not in (ShoppingStatus.PURCHASED, ShoppingStatus.STOCKED): item.status = ShoppingStatus.ON_LIST
        item.quantity, item.updated_by = required, actor_id
    elif item and item.status in (ShoppingStatus.NEEDED, ShoppingStatus.ON_LIST):
        db.delete(item)
def duplicate(db: Session, operation_id: UUID | None):
    return bool(operation_id and db.scalar(select(Transaction.id).where(Transaction.client_operation_id == operation_id)))
def add_audit(db: Session, product_id: int, user_id: int, event: str, delta: int, operation_id: UUID | None, reason: str | None, inventory_id: int | None = None):
    db.add(Transaction(product_id=product_id, user_id=user_id, inventory_id=inventory_id, event=event, quantity_delta=delta, reason=reason, client_operation_id=operation_id))
def expiration_level(expiration: date) -> str:
    days = (expiration - date.today()).days
    if days < 0: return "Abgelaufen"
    if days <= 3: return "Dringend"
    if days <= 7: return "Bald"
    return "Demnächst"
def ai_prompt(db: Session) -> str:
    rows = db.execute(select(Inventory, Product.name, Product.unit).join(Product).where(Inventory.status == InventoryStatus.ACTIVE).order_by(Inventory.expiration_date.is_(None), Inventory.expiration_date, Product.name)).all()
    expiring, remaining = [], []
    for entry, name, unit in rows:
        text = f"- {name}, {entry.quantity} {unit}"
        if entry.expiration_date:
            text += f", MHD {entry.expiration_date.strftime('%d.%m.%Y')} ({expiration_level(entry.expiration_date)})"
            if entry.expiration_date <= date.today() + timedelta(days=14): expiring.append(text)
            else: remaining.append(text)
        else: remaining.append(text)
    return "\n".join([
        "Erstelle 3 Rezeptvorschläge aus meinem Lebensmittelvorrat.", "", "Priorität: Verwende zuerst Lebensmittel, die bald ablaufen.",
        "", "Bald ablaufend:", *(expiring or ["- Keine Lebensmittel mit MHD innerhalb der nächsten 14 Tage."]),
        "", "Weitere vorhandene Lebensmittel:", *(remaining or ["- Keine weiteren aktiven Lebensmittel erfasst."]),
        "", "Bitte:", "- bevorzuge Lebensmittel mit kurzem MHD", "- verwende möglichst viele vorhandene Lebensmittel",
        "- vermeide unnötige Einkäufe", "- nenne fehlende Zutaten separat", "- gib Mengen und Zubereitung an", "- berücksichtige die MHD-Reihenfolge",
    ])

@app.on_event("startup")
def startup():
    if len(JWT_SECRET) < 32 or JWT_SECRET == DEFAULT_JWT_SECRET:
        raise RuntimeError("JWT_SECRET muss ein eigener geheimer Wert mit mindestens 32 Zeichen sein.")
    for folder in (DATA_DIR / "products", DATA_DIR / "expiration-images", DATA_DIR / "backups", DATA_DIR / "exports"): folder.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    username, password = os.getenv("INITIAL_ADMIN_USERNAME"), os.getenv("INITIAL_ADMIN_PASSWORD")
    with SessionLocal() as db:
        has_users = db.scalar(select(User.id).limit(1)) is not None
        if not has_users and (not username or len(password or "") < 12):
            raise RuntimeError("Für den ersten Start sind initial_admin_username und ein mindestens 12-stelliges initial_admin_password erforderlich.")
        if username and password and not db.scalar(select(User).where(User.username == username)):
            db.add(User(username=username, password_hash=pwd_context.hash(password), role=UserRole.ADMIN)); db.commit()

@app.get("/", tags=["system"])
def root(): return {"application": "FoodStock", "status": "ok", "version": API_VERSION}
@app.get("/health", tags=["system"])
def health():
    try:
        with engine.connect() as con: con.exec_driver_sql("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception: raise HTTPException(503, "Datenbank nicht erreichbar")
@app.get("/database-configured", tags=["system"])
def database_configured():
    """Compatibility endpoint for the initial add-on installation check.

    Passwords are intentionally never returned.
    """
    return {"database": engine.url.database, "driver": engine.url.drivername, "host": engine.url.host, "port": engine.url.port}
@app.get("/dashboard", tags=["dashboard"])
def dashboard(_: CurrentUser, db: DB):
    active_count = int(db.scalar(select(func.coalesce(func.sum(Inventory.quantity), 0)).where(Inventory.status == InventoryStatus.ACTIVE)) or 0)
    expiring_rows = list(db.scalars(select(Inventory).where(Inventory.status == InventoryStatus.ACTIVE, Inventory.expiration_date.is_not(None), Inventory.expiration_date <= date.today() + timedelta(days=14))))
    shopping_count = int(db.scalar(select(func.count()).select_from(ShoppingListItem).where(ShoppingListItem.status.in_((ShoppingStatus.NEEDED, ShoppingStatus.ON_LIST)))) or 0)
    return {"inventory_units": active_count, "expiring": {"expired": sum(i.expiration_date < date.today() for i in expiring_rows), "urgent": sum(date.today() <= i.expiration_date <= date.today() + timedelta(days=3) for i in expiring_rows), "soon": sum(date.today() + timedelta(days=4) <= i.expiration_date <= date.today() + timedelta(days=7) for i in expiring_rows), "upcoming": sum(date.today() + timedelta(days=8) <= i.expiration_date <= date.today() + timedelta(days=14) for i in expiring_rows)}, "shopping_items": shopping_count}
@app.get("/ai/prompt", tags=["recipes"])
def recipe_prompt(_: CurrentUser, db: DB):
    return {"prompt": ai_prompt(db)}

@app.post("/auth/token", response_model=Token, tags=["auth"])
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not user.active or not pwd_context.verify(form.password, user.password_hash): raise HTTPException(401, "Benutzername oder Passwort ungültig", headers={"WWW-Authenticate": "Bearer"})
    expires = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES_HOURS)
    return Token(access_token=jwt.encode({"sub": str(user.id), "role": user.role.value, "exp": expires}, JWT_SECRET, algorithm="HS256"))
@app.get("/auth/me", response_model=UserOut, tags=["auth"])
def me(user: CurrentUser): return user
@app.get("/users", response_model=list[UserOut], tags=["users"])
def users(_: Admin, db: DB): return list(db.scalars(select(User).order_by(User.username)))
@app.post("/users", response_model=UserOut, status_code=201, tags=["users"])
def create_user(data: UserCreate, _: Admin, db: DB):
    if db.scalar(select(User).where(User.username == data.username)): raise HTTPException(409, "Benutzername existiert bereits")
    user = User(username=data.username, password_hash=pwd_context.hash(data.password), role=data.role); db.add(user); db.commit(); db.refresh(user); return user
@app.patch("/users/{user_id}", response_model=UserOut, tags=["users"])
def update_user(user_id: int, data: UserUpdate, actor: Admin, db: DB):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "Benutzer nicht gefunden")
    if user.id == actor.id and data.active is False: raise HTTPException(422, "Der eigene Benutzer kann nicht deaktiviert werden")
    if data.password: user.password_hash = pwd_context.hash(data.password)
    if data.role is not None: user.role = data.role
    if data.active is not None: user.active = data.active
    db.commit(); db.refresh(user); return user

@app.get("/storage-locations", response_model=list[LocationOut], tags=["locations"])
def locations(_: CurrentUser, db: DB): return list(db.scalars(select(StorageLocation).where(StorageLocation.active).order_by(StorageLocation.name)))
@app.post("/storage-locations", response_model=LocationOut, status_code=201, tags=["locations"])
def create_location(data: LocationIn, _: Admin, db: DB):
    location = StorageLocation(**data.model_dump()); db.add(location); db.commit(); db.refresh(location); return location
@app.patch("/storage-locations/{location_id}", response_model=LocationOut, tags=["locations"])
def update_location(location_id: int, data: LocationUpdate, _: Admin, db: DB):
    location = db.get(StorageLocation, location_id)
    if not location: raise HTTPException(404, "Lagerort nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(location, key, value)
    db.commit(); db.refresh(location); return location

@app.get("/products", response_model=list[ProductOut], tags=["products"])
def products(_: CurrentUser, db: DB, include_inactive: bool = False):
    statement = select(Product).order_by(Product.name)
    if not include_inactive: statement = statement.where(Product.active)
    return [product_out(db, p) for p in db.scalars(statement)]
@app.get("/products/{product_id}", response_model=ProductOut, tags=["products"])
def product(product_id: int, _: CurrentUser, db: DB):
    p = ensure_product(db, product_id); return product_out(db, p)
@app.post("/products", response_model=ProductOut, status_code=201, tags=["products"])
def create_product(data: ProductIn, _: CurrentUser, db: DB):
    if data.barcode and db.scalar(select(Product).where(Product.barcode == data.barcode)): raise HTTPException(409, "Barcode existiert bereits")
    p = Product(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return product_out(db, p)
@app.patch("/products/{product_id}", response_model=ProductOut, tags=["products"])
def patch_product(product_id: int, data: ProductUpdate, _: Admin, db: DB):
    p = ensure_product(db, product_id)
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(p, key, value)
    db.commit(); db.refresh(p); return product_out(db, p)
@app.delete("/products/{product_id}", tags=["products"])
def deactivate_product(product_id: int, _: Admin, db: DB):
    p = ensure_product(db, product_id); p.active = False; db.commit()
    return {"status": "deactivated", "id": product_id}
@app.post("/products/{product_id}/image", response_model=ProductOut, tags=["products"])
async def product_image(product_id: int, file: UploadFile, _: Admin, db: DB):
    p = ensure_product(db, product_id)
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}: raise HTTPException(415, "Nur JPEG, PNG und WebP sind erlaubt")
    suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
    content = await file.read()
    if len(content) > 10 * 1024 * 1024: raise HTTPException(413, "Bild ist größer als 10 MB")
    target = DATA_DIR / "products" / f"{product_id}{suffix}"; target.write_bytes(content)
    p.image_path = str(target.relative_to(DATA_DIR)); db.commit(); db.refresh(p); return product_out(db, p)

@app.get("/scan/{barcode}", tags=["products"])
async def scan(barcode: str, _: CurrentUser, db: DB):
    local = db.scalar(select(Product).where(Product.barcode == barcode))
    if local: return {"found": True, "source": "local", "product": product_out(db, local)}
    try:
        async with httpx.AsyncClient(timeout=5) as client: response = await client.get(f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json", params={"fields": "product_name,brands,categories,image_url"})
        data = response.json(); item = data.get("product", {}) if data.get("status") == 1 else {}
    except (httpx.HTTPError, ValueError): item = {}
    return {"found": False, "source": "openfoodfacts" if item else None, "suggestion": {"barcode": barcode, "name": item.get("product_name"), "manufacturer": item.get("brands"), "category": item.get("categories"), "remote_image_url": item.get("image_url")} if item else None}

@app.post("/inventory", status_code=201, tags=["inventory"])
def add_inventory(data: InventoryIn, user: CurrentUser, db: DB):
    if duplicate(db, data.client_operation_id): return {"status": "already_applied"}
    p = ensure_product(db, data.product_id); location_id = data.storage_location_id or p.default_storage_location_id
    entry = Inventory(product_id=p.id, quantity=data.quantity, expiration_date=data.expiration_date, storage_location_id=location_id, added_by=user.id)
    db.add(entry); db.flush(); add_audit(db, p.id, user.id, "added", data.quantity, data.client_operation_id, "eingelagert", entry.id); update_shopping(db, p, user.id); db.commit()
    return {"status": "created", "inventory_id": entry.id, "stock": stock(db, p.id)}
@app.post("/products/{product_id}/consume", tags=["inventory"])
def consume(product_id: int, data: ConsumeIn, user: CurrentUser, db: DB):
    if duplicate(db, data.client_operation_id): return {"status": "already_applied", "stock": stock(db, product_id)}
    p = ensure_product(db, product_id); remaining = data.quantity
    entries = list(db.scalars(select(Inventory).where(Inventory.product_id == product_id, Inventory.status == InventoryStatus.ACTIVE).order_by(Inventory.expiration_date.is_(None), Inventory.expiration_date, Inventory.added_at).with_for_update()))
    for entry in entries:
        used = min(remaining, entry.quantity); entry.quantity -= used; remaining -= used
        if entry.quantity == 0: entry.status, entry.consumed_at = InventoryStatus.CONSUMED, datetime.now(timezone.utc)
        add_audit(db, p.id, user.id, "consumed", -used, data.client_operation_id if remaining == 0 else None, data.reason, entry.id)
        if not remaining: break
    if remaining:
        missing = Inventory(product_id=p.id, quantity=remaining, status=InventoryStatus.MISSING, added_by=user.id); db.add(missing); db.flush(); add_audit(db, p.id, user.id, "consumed", -remaining, data.client_operation_id, data.reason, missing.id)
    update_shopping(db, p, user.id); db.commit(); return {"status": "consumed", "stock": stock(db, p.id)}
@app.post("/products/{product_id}/correct", tags=["inventory"])
def correct(product_id: int, data: CorrectIn, user: Admin, db: DB):
    if data.quantity_delta == 0: raise HTTPException(422, "Korrektur darf nicht 0 sein")
    if duplicate(db, data.client_operation_id): return {"status": "already_applied", "stock": stock(db, product_id)}
    p = ensure_product(db, product_id); state = InventoryStatus.ACTIVE if data.quantity_delta > 0 else InventoryStatus.MISSING
    entry = Inventory(product_id=p.id, quantity=abs(data.quantity_delta), status=state, added_by=user.id); db.add(entry); db.flush(); add_audit(db, p.id, user.id, "corrected", data.quantity_delta, data.client_operation_id, data.reason, entry.id); update_shopping(db, p, user.id); db.commit(); return {"status": "corrected", "stock": stock(db, p.id)}

@app.get("/inventory", tags=["inventory"])
def inventory(_: CurrentUser, db: DB, status_filter: InventoryStatus = InventoryStatus.ACTIVE):
    rows = db.execute(select(Inventory, Product.name, Product.unit).join(Product).where(Inventory.status == status_filter).order_by(Inventory.expiration_date.is_(None), Inventory.expiration_date)).all()
    return [{"id": i.id, "product_id": i.product_id, "product_name": name, "unit": unit, "quantity": i.quantity, "expiration_date": i.expiration_date, "storage_location_id": i.storage_location_id, "status": i.status} for i, name, unit in rows]
@app.get("/expiring", tags=["inventory"])
def expiring(_: CurrentUser, db: DB, days: int = Field(default=14, ge=0, le=365)):
    return db.execute(select(Inventory, Product.name).join(Product).where(Inventory.status == InventoryStatus.ACTIVE, Inventory.expiration_date.is_not(None), Inventory.expiration_date <= date.today() + timedelta(days=days)).order_by(Inventory.expiration_date)).mappings().all()

@app.get("/shopping-list", tags=["shopping"])
def shopping_list(_: CurrentUser, db: DB):
    rows = db.execute(select(ShoppingListItem, Product.name, Product.unit).join(Product).order_by(Product.name)).all()
    return [{"product_id": i.product_id, "name": name, "unit": unit, "quantity": i.quantity, "status": i.status} for i, name, unit in rows]
@app.patch("/shopping-list/{product_id}", tags=["shopping"])
def shopping_status(product_id: int, data: ShoppingUpdate, user: CurrentUser, db: DB):
    item = db.get(ShoppingListItem, product_id)
    if not item: raise HTTPException(404, "Einkaufslisteneintrag nicht gefunden")
    item.status, item.updated_by = data.status, user.id; db.commit(); return {"status": item.status}
@app.get("/transactions", tags=["audit"])
def transactions(_: Admin, db: DB, limit: int = Field(default=100, ge=1, le=500)):
    return db.execute(select(Transaction, Product.name, User.username).join(Product).join(User).order_by(Transaction.created_at.desc()).limit(limit)).mappings().all()
