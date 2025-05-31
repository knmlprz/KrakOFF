from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .dependencies import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.EventOut])
def get_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()