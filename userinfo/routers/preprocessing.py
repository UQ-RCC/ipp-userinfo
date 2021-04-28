from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()

@router.get("/preprocessingpage", response_model=udb.schemas.PreprocessingPage)
def get_preprocessingpage(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    preprocessingpage = udb.crud.get_preprocessingpage(db, username)
    # create one if not there
    if not preprocessingpage:
        preprocessingpage = udb.crud.create_preprocessingpage(db, username)
    return preprocessingpage

# this is to call after submitting jobs
# copy existing preprocessing, but create new ones
#this is to make sure jobs attached to previous preprocessing is not affected
@router.post("/preprocessingpage/preprocessing", response_model=udb.schemas.Preprocessing)
def create_preprocessing(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.create_new_processing(db, username)

@router.get("/preprocessing/{preprocessingid}/job", response_model=udb.schemas.Job)
def get_preprocessing_job(preprocessingid:int, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.get_processing_job(db, username, preprocessingid)

# create new psettings out of the given series
@router.post("/preprocessing/{preprocessingid}/psettings", response_model=udb.schemas.PSetting)
def create_new_psetting(preprocessingid:int, series_id: int, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return  udb.crud.create_new_psetting(db, username, preprocessingid, series_id)
    
# delete existing psettings
@router.delete("/psettings/{psettingid}", response_model=udb.schemas.PSetting)
def get_preprocessing(psettingid: int, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    udb.crud.delete_psetting(db, username, psettingid)


# get existing psettings
@router.get("/psettings/{psettingid}")
def delete_preprocessing(psettingid: int, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.get_psetting(db, username, psettingid)

# update existing psettings
@router.put("/psettings/{psettingid}")
def update_psetting(psettingid: int, psetting: udb.schemas.PSettingCreate, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    udb.crud.update_psetting(db, username, psettingid, psetting)


# update existing preprocessing
@router.put("/preprocessing/{preprocessingid}", response_model=udb.schemas.Preprocessing)
def update_preprocessing(preprocessing_id: int, combine: bool, outputPath: str, user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_preprocessing(db, username, preprocessing_id, combine, outputPath)


