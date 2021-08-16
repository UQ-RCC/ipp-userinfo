from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form


import userinfo.keycloak as keycloak
import logging
import userinfo.mail as mail
import userinfo.config as config
from typing import Optional
from pydantic import BaseModel


router = APIRouter()
logger = logging.getLogger('ippuserinfo')


@router.get("/user")
async def get_user(user: dict = Depends(keycloak.decode)):
    logger.debug("Querying user")
    return user

@router.get("/token")
async def get_token(token: str = Depends(keycloak.oauth2_scheme)):
    return token




@router.post("/feedback")
async def send_feedback(title: str = Form(...), contents: str = Form(...), uploadedFile: UploadFile = File(None), user: dict = Depends(keycloak.decode)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    try:
        to_emails = config.get('email', 'admins', default = "microscopes@imb.uq.edu.au").strip()
        useremail = user.get('email')
        if not useremail:
            return HTTPException(status_code=500, detail="User email cannot be empty")
        logger.info(f"sending emails to {to_emails} ")
        if uploadedFile and uploadedFile.file:
            logger.info("Attachment present")
            filecontents = await uploadedFile.read()
            mail.send_mail_with_file(to_emails, title, contents, filecontents, uploadedFile.filename, ccemail=useremail)
        else:
            logger.info("No attachment present")
            mail.send_mail(to_emails, title, contents, subtype='plain', ccemail=useremail)
    except Exception as e:
        logger.error(f"Problem sending email: {str(e)}")
        raise