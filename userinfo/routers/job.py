from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from typing import List, Optional
from sqlalchemy.orm import Session
import datetime
import userinfo.config as config

router = APIRouter()

import logging
logger = logging.getLogger('ippuserinfo')

@router.get("")
def get_jobs(   status: Optional[str] = None, 
                username: Optional[str] = None, 
                jobname: Optional[str] = None,
                submit: Optional[datetime.date] = None,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    logger.debug("Querying jobs")
    # make sure this is only available for admins
    realm_access = user.get('realm_access')
    admin = config.get('keycloak', 'admin')
    if not realm_access or not admin in realm_access.get('roles'):
        return HTTPException(status_code=401, detail="Only admins can list jobs")
    return udb.crud.filter_jobs(db, status, username, jobname, submit)


@router.get("/{jobid}", response_model=udb.schemas.Job)
def get_job(    jobid: str,
                db: Session = Depends(udb.get_db),
                ):
    logger.debug("Querying job %s" %(jobid))
    return udb.crud.get_job(db, jobid)


@router.put("/{jobid}")
def update_job(    jobid: str,
                jobdata: udb.schemas.JobCreate,
                db: Session = Depends(udb.get_db)):
    logger.debug("Updating job %s, new status: %s" %(jobid, jobdata.status), exc_info=True)
    try:
        return udb.crud.update_job(db, jobid, jobdata)
    except udb.crud.CannotChangeException: 
        return HTTPException(status_code=304, detail="Unchanged. job state is either in FAIL or COMPLETE")    
    except Exception as e:
        logger.error("Problem updating job", exc_info=True) 
        logger.debug(e, exc_info=True)
        return HTTPException(status_code=500, detail="Problem updating job")