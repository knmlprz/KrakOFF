from fastapi import FastAPI, HTTPException
from .auth import router as auth_router
from .content import router as content_router
from .interactions import router as interactions_router
from .database import engine, SessionLocal
from .models import Base, Content
from datetime import date, time
from fastapi.middleware.cors import CORSMiddleware
import csv
from datetime import datetime

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

def import_content_from_csv(file_path: str):
    db = SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            # Sprawdź wymagane kolumny
            required_columns = ['tytul']  # Tytuł jest wymagany (nullable=False w modelu)
            optional_columns = {
                'data_rozpoczecia': None,
                'data_zakonczenia': None,
                'godzina_rozpoczecia': None,
                'czy_stale': False,
                'czy_na_zewnatrz': False
            }
            
            for row in reader:
                # Sprawdź czy wymagane kolumny istnieją
                for col in required_columns:
                    if col not in row:
                        raise ValueError(f"Brak wymaganej kolumny: {col}")
                
                # Przygotuj dane z uwzględnieniem opcjonalnych kolumn
                content_data = {
                    'tytul': row['tytul'],
                    'typ_wydarzenia': row.get('typ_wydarzenia'),
                    'data_rozpoczecia': datetime.strptime(row['data_rozpoczecia'], '%Y-%m-%d').date() if row.get('data_rozpoczecia') else None,
                    'data_zakonczenia': datetime.strptime(row['data_zakonczenia'], '%Y-%m-%d').date() if row.get('data_zakonczenia') else None,
                    'godzina_rozpoczecia': datetime.strptime(row['godzina_rozpoczecia'], '%H:%M').time() if row.get('godzina_rozpoczecia') else None,
                    'czy_stale': row.get('czy_stale', 'false').lower() == 'true',
                    'obiekt': row.get('obiekt'),
                    'ulica': row.get('ulica'),
                    'miasto': row.get('miasto'),
                    'czy_na_zewnatrz': row.get('czy_na_zewnatrz', 'false').lower() == 'true',
                    'link_do_tiktoka': row.get('link_do_tiktoka'),
                    'sciezka_do_tiktoka': row.get('sciezka_do_tiktoka'),
                    'hashtagi': row.get('hashtagi')
                }
                
                # Utwórz i dodaj rekord
                content = Content(**content_data)
                db.add(content)
            print('Załadowano model')
            db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd podczas importu danych: {str(e)}")
    finally:
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

try:
    import_content_from_csv("C:\\Users\\lolma\\OneDrive\\Desktop\\STUDIA\\KrakOFF\\app\\data\\events_tiktak.csv")
except FileNotFoundError:
    print("Plik z danymi nie został znaleziony, pomijam import")
    seed_content_data()

# Dodanie routerów
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(content_router, prefix="/content", tags=["content"])
app.include_router(interactions_router, prefix="/interactions", tags=["interactions"])

