from sqlalchemy import Column, Integer, String, ForeignKey
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
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    tags = Column(String)  # np. "dev,motywacja"

    interactions = relationship("UserInteraction", back_populates="content")


class UserInteraction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    type = Column(String)  # "like", "save", "share"

    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
