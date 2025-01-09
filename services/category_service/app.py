from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Configuración de FastAPI
app = FastAPI()

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

# Modelo de base de datos
# Modelo de base de datos
class CategoriaModel(Base):
    __tablename__ = "categorias"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    parentCategory = Column(String, ForeignKey("categorias.id"), name="parentcategory", nullable=True)  # Ajuste aquí
    imageUrl = Column(Text, name="imageurl", nullable=True)  # Ajuste aquí
    active = Column(Boolean, nullable=False, default=True)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Modelo de Pydantic
class Categoria(BaseModel):
    id: Optional[str]
    name: Optional[str]
    description: Optional[str]
    parentCategory: Optional[str]
    imageUrl: Optional[str]
    active: Optional[bool] = True

    class Config:
        orm_mode = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parentCategory: Optional[str] = None
    imageUrl: Optional[str] = None
    active: Optional[bool] = None

    class Config:
        from_attributes = True  # Para Pydantic V2


# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/api/categories", response_model=List[Categoria])
def list_categories(db: Session = Depends(get_db)):
    try:
        return db.query(CategoriaModel).all()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categories", response_model=Categoria)
def create_category(category: Categoria, db: Session = Depends(get_db)):
    try:
        new_category = CategoriaModel(
            id=category.id,
            name=category.name,
            description=category.description,
            parentCategory=category.parentCategory,
            imageUrl=category.imageUrl,
            active=category.active
        )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories/{category_id}", response_model=Categoria)
def get_category(category_id: str, db: Session = Depends(get_db)):
    try:
        category = db.query(CategoriaModel).filter(CategoriaModel.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/categories/{category_id}", response_model=Categoria)
def update_category(category_id: str, updated_category: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        category = db.query(CategoriaModel).filter(CategoriaModel.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        for key, value in updated_category.dict(exclude_unset=True).items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    try:
        category = db.query(CategoriaModel).filter(CategoriaModel.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db.delete(category)
        db.commit()
        return {"message": "Category deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
