from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL, TIMESTAMP, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import requests
import os

# URL del servicio de reseñas
REVIEW_SERVICE_URL = "http://review-service/api/reviews"

# Configuración de FastAPI
app = FastAPI()

# Configuración de la base de datos
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_USER = "kong"
POSTGRES_PASSWORD = "kongpassword"
POSTGRES_DB = "kong"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

# Modelo de la base de datos para productos
class ProductoModel(Base):
    __tablename__ = "productos"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String, ForeignKey("categorias.id"), nullable=True)
    animaltype = Column(String, name="animaltype", nullable=True)  # Mapeo a minúsculas
    brand = Column(String, nullable=True)
    stock = Column(Integer, nullable=False)
    images = Column(Text, nullable=True)    
    averagerating = Column(DECIMAL(3, 2), name="averagerating", nullable=True)  # Mapeo a minúsculas
    createdat = Column(TIMESTAMP, name="createdat", nullable=False, default=datetime.utcnow)
    updatedat = Column(TIMESTAMP, name="updatedat", nullable=False, default=datetime.utcnow)


class CategoriaModel(Base):
    __tablename__ = "categorias"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    parentCategory = Column(String, ForeignKey("categorias.id"), nullable=True)
    imageUrl = Column(Text, nullable=True)
    active = Column(Integer, nullable=False, default=1)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Modelos de Pydantic para validación
class Producto(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    animaltype: Optional[str]
    brand: Optional[str]
    stock: int
    images: Optional[str]
    averagerating: Optional[float]
    createdat: Optional[datetime] = None
    updatedat: Optional[datetime] = None

    class Config:
        orm_mode = True

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints para el servicio de productos
@app.get("/api/products", response_model=List[Producto])
def list_products(db: Session = Depends(get_db)):
    try:
        products = db.query(ProductoModel).all()
        return products
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", response_model=Producto)
def create_product(product: Producto, db: Session = Depends(get_db)):
    try:
        new_product = ProductoModel(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
def get_product_with_reviews(product_id: str, db: Session = Depends(get_db)):
    try:
        product = db.query(ProductoModel).filter(ProductoModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        response = requests.get(f"{REVIEW_SERVICE_URL}/{product_id}")
        response.raise_for_status()
        reviews = response.json()

        return {
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category,
                "animaltype": product.animaltype,
                "brand": product.brand,
                "stock": product.stock,
                "images": product.images,
                "averagerating": product.averagerating,
                "createdat": product.createdat,
                "updatedat": product.updatedat
            },
            "reviews": reviews
        }
    except HTTPException as e:
        raise e
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_id}", response_model=Producto)
def update_product(product_id: str, product: Producto, db: Session = Depends(get_db)):
    try:
        existing_product = db.query(ProductoModel).filter(ProductoModel.id == product_id).first()
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in product.dict(exclude_unset=True).items():
            setattr(existing_product, key, value)
        db.commit()
        db.refresh(existing_product)
        return existing_product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    try:
        product = db.query(ProductoModel).filter(ProductoModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
