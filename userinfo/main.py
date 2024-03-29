import logging

import userinfo.keycloak as keycloak

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from .routers import user, job, fileexplorer, decon, version, converter, preprocessing, macro, configuration
import userinfo.config as config
from logging.handlers import TimedRotatingFileHandler
import json

logger = logging.getLogger('ippuserinfo')
logger.setLevel(logging.DEBUG)

log_file = config.get('logging', 'log_file', default = "/var/log/ippuserinfo-rs.log")
fh = TimedRotatingFileHandler(log_file, when='midnight',backupCount=7)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logging.getLogger("uvicorn.access").addHandler(fh)
# logging.getLogger("uvicorn.error").addHandler(fh)
logging.getLogger("uvicorn").addHandler(fh)


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

# convert page
userinfoapi.include_router(
    converter.router,
    prefix="/preferences", 
    tags=["convert"], 
    responses={404: {"description": "Not found"}},
)

# preprocessing page
userinfoapi.include_router(
    preprocessing.router,
    prefix="/preferences", 
    tags=["preprocessing"], 
    responses={404: {"description": "Not found"}},
)

# macro page
userinfoapi.include_router(
    macro.router,
    prefix="/preferences", 
    tags=["macro"], 
    responses={404: {"description": "Not found"}},
)

# configuration page
userinfoapi.include_router(
    configuration.router,
    prefix="/preferences", 
    tags=["configuration"], 
    responses={404: {"description": "Not found"}},
)


keycloakrealm: dict = keycloak.realm
keycloak_openid: dict = keycloak.keycloak_openid
oauth2_scheme: dict = keycloak.oauth2_scheme


logger.info("Start ippuserinfo")
logger.info("----Keycloak----")
logger.info(vars(keycloakrealm))
logger.info(vars(keycloak_openid))
logger.info(vars(oauth2_scheme))
logger.info("----Keycloak end----")

