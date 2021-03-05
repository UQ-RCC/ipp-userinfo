from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter()

import logging
logger = logging.getLogger('ippuserinfo')

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
    logger.debug("Updating job %s, new status: %s" %(jobid, jobdata.status))
    try:
        return udb.crud.update_job(db, jobid, jobdata)
    except udb.crud.CannotChangeException: 
        return HTTPException(status_code=304, detail="Unchanged. job state is either in FAIL or COMPLETE")    
    except Exception as e:
        logger.debug("Problem updating job") 
        logger.debug(e)
        return HTTPException(status_code=500, detail="Problem updating job"

    
