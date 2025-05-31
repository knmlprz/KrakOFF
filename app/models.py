from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Date, Time
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
    title = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    long_description = Column(Text, nullable=True)
    date = Column(Date, nullable=True)  # oddzielna kolumna dla daty
    time = Column(Time, nullable=True)  # oddzielna kolumna dla czasu
    location = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # np. "muzyka,koncert"
    category = Column(String, nullable=True)
    price = Column(Float, nullable=True)  # zmieniono z 'ticket_price' na 'price', by pasowało do schemas.py
    weather = Column(String, nullable=True)

    interactions = relationship("UserInteraction", back_populates="content")


class UserInteraction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    type = Column(String)

    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
