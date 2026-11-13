from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()

@router.get("/tera", response_model=Optional[udb.schemas.Terastitcher])
def get_teraData(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db), path: Optional[str] = None):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    tera_data = udb.crud.get_tera(db, username,path)
    return tera_data

@router.post("/tera", response_model=udb.schemas.Terastitcher)
def create_new_terastitcher(payload:udb.schemas.TerastitcherCreate, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.create_new_terastitcher(db, username, payload)
    
@router.put("/tera/{tera_id}", response_model=udb.schemas.Terastitcher)
def update_terastitcher(tera_id:int, payload:udb.schemas.TerastitcherCreate, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_terastitcher(db, username, tera_id, payload)

######## job
@router.post("/tera/jobs", response_model=udb.schemas.Job)
def create_tera_job(tera_id: int, sendemail: bool, user: dict = Depends(keycloak.decode), 
                    db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    email = user.get('email')
    return udb.crud.create_tera_and_job(db, username, email, tera_id, sendemail)
