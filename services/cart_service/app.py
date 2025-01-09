from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Text, DECIMAL, ForeignKey, TIMESTAMP, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pydantic import Field
import uuid
import requests
import os
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSON

# Configuración de FastAPI
app = FastAPI()

# Configuración de la base de datos
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_USER = "kong"
POSTGRES_PASSWORD = "kongpassword"
POSTGRES_DB = "kong"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Configuración de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class CarritoModel(Base):
    __tablename__ = "carrito"
    id = Column(Integer, primary_key=True, autoincrement=True)  # Cambiado a Integer y configurado como autoincremental
    user_id = Column(String(255), ForeignKey("usuarios.id") ,nullable=False)
    items = Column(Text, nullable=False)
    totalamount = Column(DECIMAL(10, 2), nullable=False)
    createdat = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updatedat = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

# Modelos de base de datos
class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    firstname = Column(String)
    lastname = Column(String)
    phonenumber = Column(String)
    role = Column(String, nullable=False)
    createdat = Column(TIMESTAMP, nullable=True, default=datetime.utcnow)
    lastlogin = Column(TIMESTAMP, nullable=True)

class ProductoModel(Base):
    __tablename__ = "productos"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    animaltype = Column(String, name="animaltype", nullable=True)  # Mapeo a minúsculas
    brand = Column(String, nullable=True)
    stock = Column(Integer, nullable=False)
    images = Column(Text, nullable=True)    
    averagerating = Column(DECIMAL(3, 2), name="averagerating", nullable=True)  # Mapeo a minúsculas
    createdat = Column(TIMESTAMP, name="createdat", nullable=False, default=datetime.utcnow)
    updatedat = Column(TIMESTAMP, name="updatedat", nullable=False, default=datetime.utcnow)



# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Modelo de Pydantic
class Carrito(BaseModel):
    id: int 
    user_id: str
    items: str
    totalamount: float
    createdat: Optional[datetime] = None
    updatedat: Optional[datetime] = None

    class Config:
        from_attributes = True
        
class CarritoUpdate(BaseModel):
    user_id: Optional[str] = None
    items: Optional[str] = None
    totalamount: Optional[float] = None
    createdat: Optional[datetime] = None
    updatedat: Optional[datetime] = None

    class Config:
        from_attributes = True  # Para Pydantic V2

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service/api/products")

@app.get("/api/cart", response_model=List[Carrito])
def list_carts(db: Session = Depends(get_db)):
    try:
        return db.query(CarritoModel).all()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cart", response_model=Carrito)
def create_cart(cart: Carrito, db: Session = Depends(get_db)):
    try:
        items = eval(cart.items)
        total_amount = 0

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            # Validar los datos del item
            if not product_id or not isinstance(quantity, int) or quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Each item must have a valid product_id and a positive quantity"
                )

            # Obtener el producto de la base de datos
            product = db.query(ProductoModel).filter(ProductoModel.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {product_id} not found"
                )

            # Validar el stock disponible
            if product.stock < quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {product_id}. Available: {product.stock}"
                )

            # Calcular el total y reducir el stock
            total_amount += product.price * quantity

        # Crear el nuevo carrito
        new_cart = CarritoModel(
            user_id=cart.user_id,
            items=cart.items,
            totalamount=total_amount,
        )
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cart/{cart_id}", response_model=Carrito)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    try:
        cart = db.query(CarritoModel).filter(CarritoModel.id == cart_id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        return cart
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/cart/{cart_id}", response_model=Carrito)
def update_cart(cart_id: int, updated_cart: CarritoUpdate, db: Session = Depends(get_db)):
    try:
        cart = db.query(CarritoModel).filter(CarritoModel.id == cart_id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        for key, value in updated_cart.dict(exclude_unset=True).items():
            setattr(cart, key, value)
        db.commit()
        db.refresh(cart)
        return cart
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cart/{cart_id}")
def delete_cart(cart_id: str, db: Session = Depends(get_db)):
    try:
        cart = db.query(CarritoModel).filter(CarritoModel.id == cart_id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        db.delete(cart)
        db.commit()
        return {"message": "Cart deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
