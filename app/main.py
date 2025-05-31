from fastapi import FastAPI
from .auth import router as auth_router
from .content import router as content_router
from .interactions import router as interactions_router
from .database import engine, SessionLocal
from .models import Base
from . import models
from datetime import date, time  # ← poprawka: importujemy date i time

def seed_content_data():
    db = SessionLocal()
    if not db.query(models.Content).first():
        sample = models.Content(
            title="Event testowy",
            short_description="Opis krótki",
            long_description="Opis długi i szczegółowy",
            date=date(2025, 6, 1),
            time=time(18, 0),
            location="Kraków",
            tags="test,kultura",
            category="konferencja",
            price=0.0,
            weather="pochmurno"
        )
        db.add(sample)
        db.commit()
    db.close()

Base.metadata.create_all(bind=engine)
seed_content_data()  # ← nie zapomnij wywołać funkcji

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(content_router, prefix="/content", tags=["content"])
app.include_router(interactions_router, prefix="/interactions", tags=["interactions"])
