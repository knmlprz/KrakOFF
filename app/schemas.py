from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional, Literal


class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class ContentOut(BaseModel):
    id: int
    tytul: str
    typ_wydarzenia: Optional[str]
    data_rozpoczecia: Optional[date]
    data_zakonczenia: Optional[date]
    godzina_rozpoczecia: Optional[time]
    czy_stale: Optional[bool]
    obiekt: Optional[str]
    ulica: Optional[str]
    miasto: Optional[str]
    czy_na_zewnatrz: Optional[bool]
    link_do_tiktoka: Optional[str]
    sciezka_do_tiktoka: Optional[str]
    hashtagi: Optional[str]

    model_config = {
        "from_attributes": True
    }


class EventOut(BaseModel):
    id: int
    tytul: str
    typ_wydarzenia: Optional[str]
    data_rozpoczecia: Optional[date]
    data_zakonczenia: Optional[date]
    godzina_rozpoczecia: Optional[time]
    czy_stale: Optional[bool]
    obiekt: Optional[str]
    ulica: Optional[str]
    miasto: Optional[str]
    czy_na_zewnatrz: Optional[bool]
    link_do_obrazka: Optional[str]  # Zmienione
    sciezka_do_obrazka: Optional[str]  # Zmienione
    hashtagi: Optional[str]

    model_config = {
        "from_attributes": True
    }

class ContentDetail(ContentOut):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class InteractionCreate(BaseModel):
    content_id: int
    type: Literal["like", "save", "share"]
