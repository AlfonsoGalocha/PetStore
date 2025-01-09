from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL, TIMESTAMP, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
import json
import os

# Configuración de FastAPI
app = FastAPI()

# Configuración de la base de datos
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_USER = "kong"
POSTGRES_PASSWORD = "kongpassword"
POSTGRES_DB= "kong"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class PedidoModel(Base):
    __tablename__ = "pedidos"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("usuarios.id"), nullable=False)
    items = Column(Text, nullable=False)  # Almacena los items en formato JSON
    totalamount = Column(DECIMAL(10, 2), nullable=False)
    shipping_address = Column(Text, nullable=False)
    paymentmethod = Column(String, nullable=False)
    paymentstatus = Column(String, nullable=False)
    orderstatus = Column(String, nullable=False, default="pending")
    createdat = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updatedat = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)


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

class AddressModel(Base):
    __tablename__ = "direcciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String)
    country = Column(String, nullable=False)
    user_email = Column(String, nullable=False, index=True)

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

class CarritoModel(Base):
    __tablename__ = "carrito"
    id = Column(Integer, primary_key=True, autoincrement=True)  # Cambiado a Integer y configurado como autoincremental
    user_id = Column(String(255), ForeignKey("usuarios.id") ,nullable=False)
    items = Column(Text, nullable=False)
    totalamount = Column(DECIMAL(10, 2), nullable=False)
    createdat = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updatedat = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


# Crear las tablas
Base.metadata.create_all(bind=engine)

# Modelos de Pydantic
class OrderItem(BaseModel):
    productId: str = Field(..., alias="product_id")
    quantity: int


class OrderRequest(BaseModel):
    user_id: str
    paymentmethod: str
    shipping_address: dict

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    totalamount: float
    paymentmethod: str
    paymentstatus: str
    orderstatus: str
    createdat: datetime
    updatedat: datetime

# Dependencia para la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas de la API
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service/api/products")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service/api/users")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart-service/api/carts")

@app.post("/api/orders", response_model=OrderResponse)
def create_order(order_request: OrderRequest, db: Session = Depends(get_db)):
    try:
        # 1. Obtener la dirección del usuario desde la tabla de Direcciones
        user_address = db.query(AddressModel).filter(AddressModel.user_id == order_request.user_id).first()
        if not user_address:
            raise HTTPException(status_code=404, detail="User address not found")
        
        # Construir la dirección de la base de datos
        stored_address = {
            "street": user_address.street,
            "city": user_address.city,
            "state": user_address.state,
            "country": user_address.country,
        }

        # Comparar la dirección proporcionada con la almacenada
        if stored_address != order_request.shipping_address:
            raise HTTPException(
                status_code=400, 
                detail="Provided address does not match the user's stored address"
            )

        # 2. Obtener los ítems del carrito directamente desde la base de datos
        cart = db.query(CarritoModel).filter(CarritoModel.user_id == order_request.user_id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        cart_items = eval(cart.items)  # Convertir el string JSON a una lista de ítems

        # 3. Reducir el stock de los productos directamente en la base de datos de Productos
        total_amount = 0
        for item in cart_items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product = db.query(ProductoModel).filter(ProductoModel.id == product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
            if product.stock < quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product {product_id}. Available: {product.stock}")

            # Reducir el stock y calcular el total
            product.stock -= quantity
            total_amount += product.price * quantity

        # Guardar los cambios en los productos
        db.commit()

        # 4. Crear el pedido en la base de datos de Pedidos
        new_order = PedidoModel(
            id=str(uuid.uuid4()),
            user_id=order_request.user_id,
            items=json.dumps(cart_items),
            totalamount=total_amount,
            paymentmethod=order_request.paymentmethod,
            paymentstatus="pending",
            orderstatus="pending",
            shipping_address=json.dumps(stored_address),
            createdat=datetime.utcnow(),
            updatedat=datetime.utcnow(),
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return OrderResponse(
            id=new_order.id,
            user_id=new_order.user_id,
            items=cart_items,
            totalamount=new_order.totalamount,
            paymentmethod=new_order.paymentmethod,
            paymentstatus=new_order.paymentstatus,
            orderstatus=new_order.orderstatus,
            createdat=new_order.createdat,
            updatedat=new_order.updatedat,
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders", response_model=List[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(PedidoModel).all()
        response = []

        for order in orders:
            try:
                # Cargar los ítems del pedido
                items = json.loads(order.items)

                # Convertir a un formato estándar con 'product_id'
                items = [
                    {
                        "product_id": item.get("product_id") or item.get("productid"),
                        "quantity": item["quantity"]
                    }
                    for item in items
                ]
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid JSON format for items")

            response.append(
                OrderResponse(
                    id=order.id,
                    user_id=order.user_id,
                    items=items,
                    totalamount=float(order.totalamount),
                    paymentmethod=order.paymentmethod,
                    paymentstatus=order.paymentstatus,
                    orderstatus=order.orderstatus,
                    createdat=order.createdat,
                    updatedat=order.updatedat,
                )
            )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/{orderId}", response_model=OrderResponse)
def get_order(orderId: str, db: Session = Depends(get_db)):
    try:
        order = db.query(PedidoModel).filter(PedidoModel.id == orderId).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        try:
            items = json.loads(order.items)
            items = [OrderItem(productid=item["productId"], quantity=item["quantity"]) for item in items]
        except (KeyError, json.JSONDecodeError) as e:
            raise HTTPException(status_code=500, detail=f"Error processing items: {str(e)}")

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            items=items,
            totalamount=float(order.totalamount),
            paymentmethod=order.paymentmethod,
            paymentstatus=order.paymentstatus,
            orderstatus=order.orderstatus,
            createdat=order.createdat,
            updatedat=order.updatedat,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders/{orderId}/cancel")
def cancel_order(orderId: str, db: Session = Depends(get_db)):
    try:
        order = db.query(PedidoModel).filter(PedidoModel.id == orderId).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.orderstatus != "pending":
            raise HTTPException(status_code=400, detail="Order cannot be cancelled")

        order.orderstatus = "cancelled"
        order.updatedat = datetime.utcnow()
        db.commit()
        return {"message": "Order cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
