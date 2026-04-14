# api.py - Versión corregida con orden correcto
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import os
import hashlib
import secrets

# ========== CONFIGURACIÓN ==========
SECRET_KEY = os.getenv("SECRET_KEY", "A9SdAQv0Zhvt5vnJlpcDiiAV4m4OTds48EYts0ysBcw")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

# ========== BASE DE DATOS ==========
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./apoyo_mental.db")

# ---> ¡ESTA ES LA PARTE IMPORTANTE! <---
print(f"📌 Conectando a: {'PostgreSQL' if DATABASE_URL.startswith('postgresql') else 'SQLite'}")

if DATABASE_URL.startswith("postgresql"):
    # Configuración para PostgreSQL en Render
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Configuración para SQLite local
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ========== MODELOS ==========
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# ========== DEPENDENCIA DB ==========
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== SCHEMAS ==========
class UserCreate(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ========== AUTENTICACIÓN ==========
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Funciones de hash (sin bcrypt)
def get_password_hash(password: str) -> str:
    """Hashea contraseña usando SHA256"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña"""
    try:
        salt, hash_value = hashed_password.split("$")
        test_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return test_hash == hash_value
    except:
        return False

def authenticate_user(db, username: str, password: str):
    """Autentica un usuario"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    """Crea un token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para obtener usuario actual desde el token
def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
# ========== APP ==========
app = FastAPI(title="Apoyo Mental API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ENDPOINTS ==========
@app.get("/")
async def root():
    return {"message": "Apoyo Mental API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db=Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    hashed = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "full_name": db_user.full_name,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at
    }

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, detail="Usuario o contraseña incorrectos")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name
    }
