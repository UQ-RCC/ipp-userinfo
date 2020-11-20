import logging

import userinfo.keycloak as keycloak

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .routers import user, job, preference, version

userinfoapi = FastAPI()

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
    dependencies=[Depends(keycloak.decode)],
    responses={404: {"description": "Not found"}},
)
# preference
userinfoapi.include_router(
    preference.router,
    prefix="/preferences",
    tags=["preferences"],
    dependencies=[Depends(keycloak.decode)],
    responses={404: {"description": "Not found"}},
)
# version
userinfoapi.include_router(
    version.router, 
    tags=["version"], 
    responses={404: {"description": "Not found"}},
)

