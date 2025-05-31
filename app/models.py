from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Date, Time, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    interactions = relationship("UserInteraction", back_populates="user")


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    tytul = Column(String, nullable=False)
    typ_wydarzenia = Column(String, nullable=True)
    data_rozpoczecia = Column(Date, nullable=True)
    data_zakonczenia = Column(Date, nullable=True)
    godzina_rozpoczecia = Column(Time, nullable=True)
    czy_stale = Column(Boolean, default=False)
    obiekt = Column(String, nullable=True)
    ulica = Column(String, nullable=True)
    miasto = Column(String, nullable=True)
    czy_na_zewnatrz = Column(Boolean, default=False)
    link_do_tiktoka = Column(String, nullable=True)
    sciezka_do_tiktoka = Column(String, nullable=True)
    hashtagi = Column(String, nullable=True)

    interactions = relationship("UserInteraction", back_populates="content")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    tytul = Column(String, nullable=False)
    typ_wydarzenia = Column(String, nullable=True)
    data_rozpoczecia = Column(Date, nullable=True)
    data_zakonczenia = Column(Date, nullable=True)
    godzina_rozpoczecia = Column(Time, nullable=True)
    czy_stale = Column(Boolean, default=False)
    obiekt = Column(String, nullable=True)
    ulica = Column(String, nullable=True)
    miasto = Column(String, nullable=True)
    czy_na_zewnatrz = Column(Boolean, default=False)
    link_do_obrazka = Column(String, nullable=True)  # Nowe pole zamiast link_do_tiktoka
    sciezka_do_obrazka = Column(String, nullable=True)  # Nowe pole zamiast sciezka_do_tiktoka
    hashtagi = Column(String, nullable=True)

    interactions = relationship("UserInteraction", back_populates="event")


class UserInteraction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    type = Column(String)

    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
    event = relationship("Event", back_populates="interactions") 