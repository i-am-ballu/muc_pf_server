from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return {"users": ["Ram", "Shyam", "Balram"]}
