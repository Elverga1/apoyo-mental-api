# api.py - Versión simplificada para pruebas
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API funcionando"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/register")
async def register():
    return {"message": "Endpoint de registro funcionando"}
