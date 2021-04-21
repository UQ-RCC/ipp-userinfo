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

@router.put("/convertpage", response_model=udb.schemas.ConvertPage)
def get_convertpage(convertpage: udb.schemas.ConvertPage, 
                    user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    return udb.crud.update_convertpage(db, username, convertpage)

