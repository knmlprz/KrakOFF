from fastapi import FastAPI, HTTPException
from .auth import router as auth_router
from .content import router as content_router
from .interactions import router as interactions_router
from .database import engine, SessionLocal
from .models import Base, Content, Event
from datetime import date, time
from fastapi.middleware.cors import CORSMiddleware
import csv
from datetime import datetime
from .events import router as events_router
from fastapi.staticfiles import StaticFiles




# Tworzenie aplikacji
app = FastAPI()


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lub zawężone domeny np. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tworzenie tabel w bazie danych
Base.metadata.create_all(bind=engine)


app.mount("/static/events", StaticFiles(directory="app/obrazy_wydarzen_karnet"), name="event_images")

# Seedowanie przykładowych danych
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

seed_content_data()

# Import danych z CSV
def import_content_tiktoks_from_csv(file_path: str, overwrite: bool = False):
    db = SessionLocal()
    try:
        if overwrite:
            # Usuń wszystkie istniejące rekordy
            db.query(Content).delete()
            print("Usunięto wszystkie istniejące wydarzenia")



        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            required_columns = ['tytul']

            for row in reader:
                for col in required_columns:
                    if col not in row:
                        raise ValueError(f"Brak wymaganej kolumny: {col}")

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
                    'sciezka_do_tiktoka': row.get('sciezka_do_filmiku'),
                    'hashtagi': row.get('hashtagi')
                }

                content = Content(**content_data)
                db.add(content)
            print('Załadowano tiktoki')
            db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd podczas importu danych: {str(e)}")
    finally:
        db.close()


def import_events_from_csv(file_path: str, overwrite: bool = False):
    db = SessionLocal()
    try:
        if overwrite:
            # Usuń wszystkie istniejące rekordy
            db.query(Event).delete()
            print("Usunięto wszystkie istniejące wydarzenia")



        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            for row in reader:
                event_data = {
                    'tytul': row.get('tytul', '').strip(),
                    'typ_wydarzenia': row.get('typ_wydarzenia_lista', '').strip() or None,
                    'data_rozpoczecia': datetime.strptime(row['data_rozpoczecia'], '%Y-%m-%d').date() if row.get('data_rozpoczecia') else None,
                    'data_zakonczenia': datetime.strptime(row['data_zakonczenia'], '%Y-%m-%d').date() if row.get('data_zakonczenia') else None,
                    'godzina_rozpoczecia': datetime.strptime(row['godzina_rozpoczecia'], '%H:%M').time() if row.get('godzina_rozpoczecia') else None,
                    'czy_stale': row.get('czy_stale', 'false').strip().lower() == 'true',
                    'obiekt': row.get('obiekty', '').strip() or None,
                    'ulica': row.get('ulice', '').strip() or None,
                    'miasto': row.get('miasta', '').strip() or None,
                    'czy_na_zewnatrz': row.get('czy_na_zewnatrz', 'false').strip().lower() == 'true',
                    'link_do_obrazka': row.get('link_do_obrazka_lista', '').strip() or None,
                    'sciezka_do_obrazka': row.get('sciezka_do_pobranego_obrazka', '').strip() or None,
                    'hashtagi': row.get('hashtagi', '').strip() or None
                }

                if not event_data['tytul']:
                    raise ValueError("Tytuł jest wymaganym polem i nie może być pusty")

                event = Event(**event_data)
                db.add(event)
            print('Załadowano eventy')
            db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd podczas importu eventów: {str(e)}")
    finally:
        db.close()

# Import danych z plików CSV
try:
    import_content_tiktoks_from_csv("app/data/events_tiktak.csv")
except FileNotFoundError:
    print("Plik z danymi nie został znaleziony, pomijam import")

try:
    import_events_from_csv("app/data/wydarzenia_cleaned.csv")
except FileNotFoundError:
    print("Brak pliku z danymi eventów, pomijam import")

# Dodanie routerów
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(content_router, prefix="/content", tags=["content"])
app.include_router(interactions_router, prefix="/interactions", tags=["interactions"])
app.include_router(events_router, prefix="/events", tags=["events"])
