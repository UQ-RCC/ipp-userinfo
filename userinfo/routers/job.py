from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{jobid}", response_model=udb.schemas.Job)
def get_job(    jobid: str,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db),
                ):
    username = user.get('preferred_username')
    return udb.crud.get_job(db, username, jobid)


@router.put("/{jobid}")
def update_job(    jobid: str,
                jobdata: udb.schemas.JobCreate,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.update_job(db, username, jobid, jobdata)
    
