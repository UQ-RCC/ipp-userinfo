from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()


@router.post("/configuration", response_model=udb.schemas.ApiSetting)
def save_api_setting(api: str, user: dict = Depends(keycloak.decode), 
                    db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_api_setting(db, username, api)

@router.get("/configuration", response_model=udb.schemas.ApiSetting)
def get_current_api(db: Session = Depends(udb.get_db)):
    return udb.crud.get_api(db)

