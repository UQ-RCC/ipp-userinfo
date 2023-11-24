from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()


@router.post("/configuration", response_model=udb.schemas.ConfigSetting)
def save_config_setting(api: str, metadata:str, user: dict = Depends(keycloak.decode), 
                    db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_config_setting(db, username, api, metadata )

@router.get("/configuration", response_model=udb.schemas.ConfigSetting)
def get_current_config(db: Session = Depends(udb.get_db)):
    return udb.crud.get_config(db)

