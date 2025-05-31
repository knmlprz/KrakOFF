from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/like")
def like_content(interaction: schemas.InteractionCreate,
                 db: Session = Depends(get_db),
                 user = Depends(get_current_user)):
    if interaction.type != "like":
        raise HTTPException(status_code=400, detail="Type must be 'like'")
    db_interaction = models.UserInteraction(
        user_id=user.id,
        content_id=interaction.content_id,
        type="like"
    )
    db.add(db_interaction)
    db.commit()
    return {"message": "liked"}

@router.post("/save")
def save_content(interaction: schemas.InteractionCreate,
                 db: Session = Depends(get_db),
                 user = Depends(get_current_user)):
    if interaction.type != "save":
        raise HTTPException(status_code=400, detail="Type must be 'save'")
    db_interaction = models.UserInteraction(
        user_id=user.id,
        content_id=interaction.content_id,
        type="save"
    )
    db.add(db_interaction)
    db.commit()
    return {"message": "saved"}

@router.post("/share")
def share_content(interaction: schemas.InteractionCreate,
                  db: Session = Depends(get_db),
                  user = Depends(get_current_user)):
    db_interaction = models.UserInteraction(
        user_id=user.id,
        content_id=interaction.content_id,
        type="share"
    )
    db.add(db_interaction)
    db.commit()
    return {"message": "shared"}

@router.get("/history")
def interaction_history(db: Session = Depends(get_db),
                        user = Depends(get_current_user)):
    return db.query(models.UserInteraction).filter_by(user_id=user.id).all()

@router.get("/get_info", response_model=schemas.ContentDetail)
def get_event_info(content_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Content).filter(models.Content.id == content_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
