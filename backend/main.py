# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, Base
from .routers import auth, conversations, assessments

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Apoyo Mental API",
    description="API para análisis de salud mental",
    version="2.0.0",
    docs_url="/docs"
)

# Configurar CORS correctamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(assessments.router)

@app.get("/")
async def root():
    return {"message": "Apoyo Mental API", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}