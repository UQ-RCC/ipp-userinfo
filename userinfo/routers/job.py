from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{jobid}", response_model=udb.schemas.Job)
def get_job(    jobid: str,
                db: Session = Depends(udb.get_db),
                ):
    return udb.crud.get_job(db, jobid)


@router.put("/{jobid}")
def update_job(    jobid: str,
                jobdata: udb.schemas.JobCreate,
                db: Session = Depends(udb.get_db)):
    return udb.crud.update_job(db, jobid, jobdata)
    
