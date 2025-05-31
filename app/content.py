from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .dependencies import get_db



router = APIRouter()

@router.get("/feed", response_model=List[schemas.ContentOut])
def get_feed(db: Session = Depends(get_db)):
    return db.query(models.Content).all()

from fastapi import UploadFile, File
import tempfile

@router.post("/import-from-csv")
async def import_content_from_csv_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Zapisz plik tymczasowo
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Wywołaj funkcję importującą
        import_content_from_csv(temp_file_path)
        
        return {"message": "Dane zostały zaimportowane pomyślnie"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))