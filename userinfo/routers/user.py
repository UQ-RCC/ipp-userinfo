from fastapi import APIRouter, Depends

import userinfo.keycloak as keycloak
import logging

router = APIRouter()
logger = logging.getLogger('ippuserinfo')


@router.get("/user")
async def get_user(user: dict = Depends(keycloak.decode)):
    logger.debug("Querying user")
    return user

@router.get("/token")
async def get_token(token: str = Depends(keycloak.oauth2_scheme)):
    return token