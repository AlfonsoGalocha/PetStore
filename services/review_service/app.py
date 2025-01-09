from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, TIMESTAMP, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import uuid


# Configuración de PostgreSQL
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_USER = "kong"
POSTGRES_PASSWORD = "kongpassword"
POSTGRES_DB = "kong"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Configuración de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

# Modelos de base de datos
class ReviewModel(Base):
    __tablename__ = "resenas"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String,ForeignKey("usuarios.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    productid = Column(String, ForeignKey("productos.id"), nullable=False)

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
    category = Column(String, ForeignKey("categorias.id"), nullable=True)
    animaltype = Column(String, name="animaltype", nullable=True)  # Mapeo a minúsculas
    brand = Column(String, nullable=True)
    stock = Column(Integer, nullable=False)
    images = Column(Text, nullable=True)    
    averagerating = Column(DECIMAL(3, 2), name="averagerating", nullable=True)  # Mapeo a minúsculas
    createdat = Column(TIMESTAMP, name="createdat", nullable=False, default=datetime.utcnow)
    updatedat = Column(TIMESTAMP, name="updatedat", nullable=False, default=datetime.utcnow)



# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Modelos de Pydantic
class Review(BaseModel):
    id: Optional[str] = None
    userId: str = Field(alias="user_id")
    rating: int
    comment: Optional[str] = None
    productId: Optional[str] = Field(alias="productid")

    class Config:
        allow_population_by_field_name = True

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# Endpoints
@app.get("/api/reviews/{productId}", response_model=List[Review])
def list_product_reviews(productId: str, db: Session = Depends(get_db)):
    try:
        reviews = db.query(ReviewModel).filter(ReviewModel.productid == productId).all()
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")

@app.post("/api/reviews/{productId}", response_model=Review)
def add_product_review(productId: str, review: Review, db: Session = Depends(get_db)):
    try:
        new_review = ReviewModel(
            id=str(uuid.uuid4()),  # Generar un ID único
            user_id=review.userId,
            rating=review.rating,
            comment=review.comment,
            productid=productId
        )
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding review: {str(e)}")

@app.put("/api/reviews/{productId}/{reviewId}", response_model=Review)
def update_product_review(productId: str, reviewId: str, review: Review, db: Session = Depends(get_db)):
    try:
        db_review = db.query(ReviewModel).filter(ReviewModel.id == reviewId, ReviewModel.productid == productId).first()
        if not db_review:
            raise HTTPException(status_code=404, detail="Review not found")
        db_review.rating = review.rating
        db_review.comment = review.comment
        db.commit()
        db.refresh(db_review)
        return db_review
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")

@app.delete("/api/reviews/{productId}/{reviewId}")
def delete_product_review(productId: str, reviewId: str, db: Session = Depends(get_db)):
    try:
        db_review = db.query(ReviewModel).filter(ReviewModel.id == reviewId, ReviewModel.productid == productId).first()
        if not db_review:
            raise HTTPException(status_code=404, detail="Review not found")
        db.delete(db_review)
        db.commit()
        return {"message": "Review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting review: {str(e)}")
