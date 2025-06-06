from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Store Management API"}

# Stores CRUD
@app.get("/stores", response_model=List[schemas.Store])
def read_stores(db: Session = Depends(get_db)):
    return db.query(models.Store).all()

@app.post("/stores", response_model=schemas.Store, status_code=status.HTTP_201_CREATED)
def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    # Проверка на уникальность комбинации name и address
    existing_store = db.query(models.Store).filter(
        models.Store.name == store.name,
        models.Store.address == store.address
    ).first()
    if existing_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store with this name and address already exists"
        )
    
    db_store = models.Store(name=store.name, address=store.address)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@app.get("/stores/{store_id}/products", response_model=List[schemas.Product])
def read_store_products(store_id: int, db: Session = Depends(get_db)):
    db_store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store.products

@app.put("/stores/{store_id}", response_model=schemas.Store)
def update_store(store_id: int, store: schemas.StoreCreate, db: Session = Depends(get_db)):
    db_store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Проверка на уникальность при обновлении
    if store.name != db_store.name or store.address != db_store.address:
        existing_store = db.query(models.Store).filter(
            models.Store.name == store.name,
            models.Store.address == store.address
        ).first()
        if existing_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store with this name and address already exists"
            )
    
    db_store.name = store.name
    db_store.address = store.address
    db.commit()
    db.refresh(db_store)
    return db_store

# Products CRUD
@app.get("/products", response_model=List[schemas.Product])
def read_products(store_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if store_id is not None:
        query = query.filter(models.Product.store_id == store_id)
    return query.all()

@app.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Проверка существования магазина
    db_store = db.query(models.Store).filter(models.Store.id == product.store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    
    db_product = models.Product(
        name=product.name,
        price=product.price,
        store_id=product.store_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return