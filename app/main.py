from fastapi import FastAPI
from .auth import router as auth_router
from .content import router as content_router
from .interactions import router as interactions_router
from .database import engine, SessionLocal
from .models import Base, Content
from datetime import date, time
from fastapi.middleware.cors import CORSMiddleware

def seed_content_data():
    db = SessionLocal()
    if not db.query(Content).first():
        sample = Content(
            tytul="Event testowy",
            typ_wydarzenia="konferencja",
            data_rozpoczecia=date(2025, 6, 1),
            data_zakonczenia=date(2025, 6, 2),
            godzina_rozpoczecia=time(18, 0),
            czy_stale=False,
            obiekt="Hala Expo",
            ulica="ul. Długa 1",
            miasto="Kraków",
            czy_na_zewnatrz=True,
            link_do_tiktoka="https://tiktok.com/@example",
            sciezka_do_tiktoka="/media/tiktok/event.mp4",
            hashtagi="#konferencja #krakow"
        )
        db.add(sample)
        db.commit()
    db.close()



app = FastAPI()

# Pozwól Flutterowi się łączyć (localhost i ewentualnie emulator)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji podaj konkretny frontendowy adres
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tworzenie tabel w bazie danych
Base.metadata.create_all(bind=engine)
seed_content_data()

# Tworzenie aplikacji
app = FastAPI()

# Dodanie routerów
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(content_router, prefix="/content", tags=["content"])
app.include_router(interactions_router, prefix="/interactions", tags=["interactions"])
