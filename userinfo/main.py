import logging

import userinfo.keycloak as keycloak

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from .routers import user, job, fileexplorer, decon, version

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)s] %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)


userinfoapi = FastAPI()

userinfoapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# user
userinfoapi.include_router(
    user.router, 
    tags=["user"], 
    dependencies=[Depends(keycloak.decode)], 
    responses={404: {"description": "Not found"}},
)
# job
userinfoapi.include_router(
    job.router,
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

# decon
userinfoapi.include_router(
    decon.router,
    prefix="/preferences",
    tags=["decons"],
    dependencies=[Depends(keycloak.decode)],
    responses={404: {"description": "Not found"}},
)

# fileexplorer
userinfoapi.include_router(
    fileexplorer.router,
    prefix="/preferences",
    tags=["fileexplorer"],
    dependencies=[Depends(keycloak.decode)],
    responses={404: {"description": "Not found"}},
)
# version
userinfoapi.include_router(
    version.router, 
    tags=["version"], 
    responses={404: {"description": "Not found"}},
)

logger.info("Start ippuserinfo")