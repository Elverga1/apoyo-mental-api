# api.py - Versión completa con POST
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para registro
class UserRegister(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    password: str

@app.get("/")
async def root():
    return {"message": "Apoyo Mental API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/register")
async def register(user: UserRegister):
    # Por ahora solo simula el registro
    return {
        "message": "Usuario registrado exitosamente",
        "user": {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
    }

@app.post("/login")
async def login(username: str, password: str):
    return {
        "access_token": "fake-token-123",
        "token_type": "bearer"
    }
