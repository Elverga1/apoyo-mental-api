# main.py - Punto de entrada simplificado
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Apoyo Mental API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Apoyo Mental API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
