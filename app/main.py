from fastapi import FastAPI
from .auth import router as auth_router
from .content import router as content_router
from .interactions import router as interactions_router
from .database import engine
from .models import Base
from . import models
from .database import SessionLocal

def seed_content_data():
    db = SessionLocal()
    existing = db.query(models.Content).first()
    if existing:
        db.close()
        return  # Seed już istnieje

    items = [
        models.Content(title="Jak rozwijać się jako programista", tags="programowanie,motywacja"),
        models.Content(title="5 sposobów na efektywną naukę", tags="nauka,produktywność"),
        models.Content(title="Jak budować dobre nawyki", tags="psychologia,rozwój")
    ]
    db.add_all(items)
    db.commit()
    db.close()


Base.metadata.create_all(bind=engine)
seed_content_data()

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(content_router, prefix="/content", tags=["content"])
app.include_router(interactions_router, prefix="/interactions", tags=["interactions"])
