from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True
    }

class ContentOut(BaseModel):
    id: int
    title: str
    tags: str

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class InteractionCreate(BaseModel):
    content_id: int
    type: str  # "like" lub "save"

