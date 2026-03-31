# backend/create_admin.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.database import SessionLocal
from backend.models.models import User
from backend.auth.auth import get_password_hash

def create_admin():
    db = SessionLocal()
    
    # Verificar si ya existe admin
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("⚠️ Usuario admin ya existe")
        return
    
    # Crear admin
    admin = User(
        username="WenEd",
        email="odraudeonofre156@gmail.com",
        hashed_password=get_password_hash("WenEd2816"),
        full_name="Administrador",
        is_admin=True,
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    print("✅ Usuario administrador creado:")
    print("   Usuario: admin")
    print("   Contraseña: Admin123!")

if __name__ == "__main__":
    create_admin()