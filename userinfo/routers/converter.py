from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()

@router.get("/convertpage", response_model=udb.schemas.ConvertPage)
def get_convertpage(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    convert_page = udb.crud.get_convertpage(db, username)
    # create one if not there
    if not convert_page:
        convert_page = udb.crud.create_convertpage(db, username)
    return convert_page

# call this endpoint after submitting a job
@router.post("/convertpage/convert", response_model=udb.schemas.Convert)
def create_new_convert(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    return udb.crud.create_new_convert(db, username)


@router.put("/convert/{convertid}")
def update_convert(convertid: int, convert: udb.schemas.ConvertCreate, 
                    user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    return udb.crud.update_convert(db, username, convertid, convert)

@router.get("/convertpage/convert/{convertid}")
def get_convert(convertid: int, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    return udb.crud.get_convert(db, username, convertid)


######## job
@router.get("/convert/{convertid}/job", response_model=udb.schemas.Job)
def get_convert_job(convertid: int, sendemail: bool, user: dict = Depends(keycloak.decode), 
                    db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.get_convert_job(db, username, convertid, sendemail)
