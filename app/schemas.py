from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional


class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class ContentOut(BaseModel):
    id: int
    title: str
    short_description: str
    long_description: str
    date: date
    time: time
    location: str
    tags: str
    category: str
    price: float
    weather: Optional[str] = None

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
    type: str  # "like", "save" lub "share"
