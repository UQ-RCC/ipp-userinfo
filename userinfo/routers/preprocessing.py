from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()

@router.get("/preprocessing", response_model=udb.schemas.Preprocessing)
def get_preprocessing(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    preprocessing = udb.crud.get_preprocessing(db, username)
    # create one if not there
    if not preprocessing:
        preprocessing = udb.crud.create_preprocessing(db, username)
    return preprocessing