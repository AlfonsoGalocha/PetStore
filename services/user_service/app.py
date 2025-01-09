from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, String, Integer, TIMESTAMP, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from datetime import datetime
from bcrypt import hashpw, gensalt, checkpw  
import uuid


# FastAPI app
app = FastAPI()

# Autenticación con JWT
SECRET_KEY = "21b5b0060b7f63d5922ae9de7d070f2f8e7d8e6de685f6ee3d54ba7bb8cabba0"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Modelos de Pydantic
class Usuario(BaseModel):
    id: Optional[str]
    username: str
    email: str
    password: str
    firstname: Optional[str]
    lastname: Optional[str]
    phonenumber: Optional[str]
    role: str
    createdat: Optional[datetime] = None
    lastlogin: Optional[datetime] = None

class Address(BaseModel):
    street: str
    city: str
    state: Optional[str]
    country: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

# Endpoints
@app.post("/api/users/register", response_model=Usuario)
def register_user(user: Usuario, db: Session = Depends(get_db)):
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(UsuarioModel).filter(
            (UsuarioModel.email == user.email) | (UsuarioModel.username == user.username)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email or username already exists")
        
        
        hashed_password = hash_password(user.password)


        # Crear nuevo usuario
        new_user = UsuarioModel(
            id=user.id,
            username=user.username,
            email=user.email,
            password=hashed_password,
            firstname=user.firstname,
            lastname=user.lastname,
            phonenumber=user.phonenumber,
            role=user.role,
            createdat=datetime.utcnow(),
            lastlogin=None,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        # Buscar el usuario por su email
        user = db.query(UsuarioModel).filter(UsuarioModel.email == request.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verificar si la contraseña coincide con el hash almacenado
        if not checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generar el token JWT
        token = jwt.encode({"email": user.email}, SECRET_KEY, algorithm="HS256")
        user.lastlogin = datetime.utcnow()
        db.commit()
        
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/users/profile", response_model=Usuario)
def get_user_profile(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(UsuarioModel).filter(UsuarioModel.email == current_user).first()
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/addresses", response_model=List[Address])
def list_addresses(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        addresses = db.query(AddressModel).filter(AddressModel.user_email == current_user).all()
        return addresses
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/addresses", response_model=Address)
def add_address(address: Address, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Buscar el usuario por email
        user = db.query(UsuarioModel).filter(UsuarioModel.email == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Crear la nueva dirección usando el ID del usuario
        new_address = AddressModel(
            id=str(uuid.uuid4()),
            user_id=user.id,  # Usar el ID del usuario en lugar del email
            street=address.street,
            city=address.city,
            state=address.state,
            country=address.country,
            user_email=current_user  # Esto es opcional si necesitas mantener el email
        )
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        return address
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
