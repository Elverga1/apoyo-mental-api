from fastapi import FastAPI, Request
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

@app.api_route("/register", methods=["GET", "POST", "PUT", "DELETE"])
async def register_all(request: Request):
    return {
        "method": request.method,
        "message": "Endpoint funcionando con método " + request.method
    }

@app.post("/test-post")
async def test_post():
    return {"message": "POST funcionando correctamente"}
