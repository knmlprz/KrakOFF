from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .dependencies import get_db

router = APIRouter()

@router.get("/feed", response_model=List[schemas.ContentOut])
def get_feed(db: Session = Depends(get_db)):
    return db.query(models.Content).all()
