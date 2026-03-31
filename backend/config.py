# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "V-fMK4upTc0RotN3mZXQR1qBcvG_W_FodG3Kk_rtH2A")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./apoyo_mental.db")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

settings = Settings()