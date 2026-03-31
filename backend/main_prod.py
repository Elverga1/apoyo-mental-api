# backend/main_prod.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, Base
from .routers import auth, conversations, assessments
from .config import settings
import uvicorn

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Apoyo Mental API",
    description="API para análisis de salud mental",
    version="2.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(assessments.router)

@app.get("/")
async def root():
    return {"message": "Apoyo Mental API", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)