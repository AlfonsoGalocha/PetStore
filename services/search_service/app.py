from fastapi import FastAPI, HTTPException, Query
from typing import List, Literal, Optional
from pydantic import BaseModel
from sqlalchemy import text, Column, String, Text, DECIMAL, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


app = FastAPI()

# Configuración de PostgreSQL
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_USER = "kong"
POSTGRES_PASSWORD = "kongpassword"
POSTGRES_DB = "kong"

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Configuración de SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Esquema para resultados de búsqueda
class SearchResult(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str  # Puede ser "product" o "category"

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

@app.get("/api/search", response_model=List[SearchResult])
async def search(
    q: str = Query(..., alias="q", description="Consulta de búsqueda"),
    type: Literal["productos", "categorias", "all"] = "all"
):
    """
    Realiza una búsqueda general en productos y categorías.
    """
    try:
        results = []

        async with async_session() as session:
            # Consulta productos si type es "productos" o "all"
            if type in ["productos", "all"]:
                product_query = text("""
                    SELECT id, name, description, 'product' AS type
                    FROM "productos"
                    WHERE LOWER(name) LIKE :query OR LOWER(description) LIKE :query
                """)
                try:
                    products = await session.execute(product_query, {"query": f"%{q.lower()}%"})
                    results.extend(products.mappings().all())  # Extraer como diccionarios
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error querying products: {str(e)}")

            # Consulta categorías si type es "categorias" o "all"
            if type in ["categorias", "all"]:
                category_query = text("""
                    SELECT id, name, description, 'category' AS type
                    FROM "categorias"
                    WHERE LOWER(name) LIKE :query OR LOWER(description) LIKE :query
                """)
                try:
                    categories = await session.execute(category_query, {"query": f"%{q.lower()}%"})
                    results.extend(categories.mappings().all())  # Extraer como diccionarios
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error querying categories: {str(e)}")

        if not results:
            raise HTTPException(status_code=404, detail="No results found")

        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
