from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import logging
logger = logging.getLogger('ippuserinfo')
router = APIRouter()


@router.post("/resources", response_model=udb.schemas.Resources)
def create_resource(payload:udb.schemas.ResourcesCreate, user: dict = Depends(keycloak.decode), 
                    db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    logger.debug(f"New resource resou   {payload}")
    return udb.crud.create_resource(db, username, payload )

@router.get("/resources", response_model=List[udb.schemas.Resources])
def get_current_resources(db: Session = Depends(udb.get_db)):
    return udb.crud.get_resources(db)

@router.put("/resources/{record_id}", response_model=udb.schemas.Resources)
def update_resource(record_id:int, payload:udb.schemas.ResourcesCreate, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_resource(db, username, record_id, payload)

@router.delete("/resources/{record_id}")
def delete_resource(record_id: int, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    logger.debug(f"username resource resou   {username}")
    return udb.crud.delete_resource(db, username, record_id)

