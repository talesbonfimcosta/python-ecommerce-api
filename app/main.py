import os
import secrets
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Product
from .schemas import ProductCreate, ProductPage, ProductRead, ProductUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="E-commerce Products API", version="1.0.0", lifespan=lifespan)

def require_admin(x_api_key: str | None = Header(default=None)):
    key = os.getenv("ADMIN_API_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="Admin API key is not configured")
    if not x_api_key or not secrets.compare_digest(x_api_key, key):
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/products", response_model=ProductPage)
def list_products(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), category: str | None = None, name: str | None = None, db: Session = Depends(get_db)):
    statement = select(Product)
    if category:
        statement = statement.where(Product.category == category)
    if name:
        escaped = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        statement = statement.where(Product.name.ilike(f"%{escaped}%", escape="\\"))
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = db.scalars(statement.order_by(Product.id).offset(offset).limit(limit)).all()
    return ProductPage(items=items, total=total, limit=limit, offset=offset)

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=ProductRead, status_code=201, dependencies=[Depends(require_admin)])
def create_product(payload: ProductCreate, response: Response, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product SKU already exists")
    db.refresh(product)
    response.headers["Location"] = f"/products/{product.id}"
    return product

@app.patch("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_admin)])
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is None and key != "description":
            raise HTTPException(status_code=422, detail=f"{key} cannot be null")
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
