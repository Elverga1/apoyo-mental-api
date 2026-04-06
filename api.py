# api.py - Versión completa basada en simple_api.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os

# ========== CONFIGURACIÓN ==========
SECRET_KEY = os.getenv("SECRET_KEY", "mi-clave-secreta-temporal-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

# ========== BASE DE DATOS ==========
DATABASE_URL = "sqlite:///./apoyo_mental.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ========== MODELOS ==========
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    title = Column(String, default="Nueva conversación")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer)
    role = Column(String)
    content = Column(Text)
    risk_level = Column(String, default="bajo")
    created_at = Column(DateTime, default=datetime.utcnow)

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    type = Column(String)
    score = Column(Integer)
    severity = Column(String)
    answers = Column(Text, nullable=True)
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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
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
app = FastAPI(title="Apoyo Mental API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ENDPOINTS BÁSICOS ==========
@app.get("/")
async def root():
    return {"message": "Apoyo Mental API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ========== ENDPOINTS DE AUTENTICACIÓN ==========
@app.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db=Depends(get_db)):
    # Verificar si ya existe
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    # Crear usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name
    }

# ========== ENDPOINTS DE CONVERSACIONES ==========
@app.post("/conversations")
def create_conversation(current_user: User = Depends(get_current_user), db=Depends(get_db)):
    conversation = Conversation(user_id=current_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return {"id": conversation.id, "title": conversation.title, "created_at": conversation.created_at}

@app.get("/conversations")
def get_conversations(current_user: User = Depends(get_current_user), db=Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    return conversations

@app.post("/conversations/{conv_id}/messages")
def send_message(conv_id: int, message: dict, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    # Verificar que la conversación pertenece al usuario
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Guardar mensaje del usuario
    user_msg = Message(conversation_id=conv_id, role="user", content=message.get("content", ""))
    db.add(user_msg)
    
    # Respuesta simple de IA
    response_text = "Gracias por compartir cómo te sientes. Estoy aquí para apoyarte."
    
    # Guardar respuesta
    ai_msg = Message(conversation_id=conv_id, role="assistant", content=response_text)
    db.add(ai_msg)
    
    # Actualizar fecha de conversación
    conv.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ai_msg)
    
    return {"id": ai_msg.id, "role": ai_msg.role, "content": ai_msg.content}

@app.get("/conversations/{conv_id}")
def get_conversation(conv_id: int, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at).all()
    return {"id": conv.id, "title": conv.title, "messages": messages}

# ========== ENDPOINTS DE EVALUACIONES ==========
@app.post("/assessments")
def save_assessment(assessment: dict, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    db_assessment = Assessment(
        user_id=current_user.id,
        type=assessment.get("type"),
        score=assessment.get("score"),
        severity=assessment.get("severity"),
        answers=str(assessment.get("answers", {}))
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return {"id": db_assessment.id, "message": "Evaluación guardada"}

@app.get("/assessments")
def get_assessments(current_user: User = Depends(get_current_user), db=Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.user_id == current_user.id).all()
    return assessments
