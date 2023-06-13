from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()

@router.get("/macro", response_model=udb.schemas.Macro)
def get_macroData(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    macro_data = udb.crud.get_macro(db, username)
    # create one if not there
    """ if not macro_data:
        macro_data = udb.crud.create_macro(db, username) """
    return macro_data

@router.post("/macro", response_model=udb.schemas.Macro)
def create_new_macro(payload:udb.schemas.MacroCreate, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.create_new_macro(db, username, payload)
    
@router.put("/macro/{macro_id}", response_model=udb.schemas.Macro)
def update_macro(macro_id:int, payload:udb.schemas.MacroCreate, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_macro(db, username, macro_id, payload)

######## job
@router.get("/macro/{macro_id}/job", response_model=udb.schemas.Job)
def get_macro_job(macro_id: int, sendemail: bool, user: dict = Depends(keycloak.decode), 
                    db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    email = user.get('email')
    return udb.crud.get_macro_job(db, username, email, macro_id, sendemail)
