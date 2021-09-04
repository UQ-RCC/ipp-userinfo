from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form


import userinfo.keycloak as keycloak
import logging
import userinfo.mail as mail
import userinfo.config as config
from typing import Optional
from pydantic import BaseModel
import swiftclient
import shortuuid
import requests
import json
import os

router = APIRouter()
logger = logging.getLogger('ippuserinfo')

if config.get('github', 'enabled', default='false').strip() == 'true':
    user = config.get('github', 'swift_username')
    key = config.get('github', 'swift_password')
    auth_url = config.get('github', 'swift_auth_url')
    auth_version = config.get('github', 'swift_auth_v')
    os_options = {
        'user_domain_name': config.get('github', 'swift_user_domain_name'),
        'project_domain_id':config.get('github', 'swift_project_domain_id'),
        'project_name': config.get('github', 'swift_project_name')
    }
    swift = swiftclient.Connection(user=user,key=key,os_options=os_options, auth_version=auth_version,authurl=auth_url)


@router.get("/user")
async def get_user(user: dict = Depends(keycloak.decode)):
    logger.debug("Querying user")
    return user

@router.get("/token")
async def get_token(token: str = Depends(keycloak.oauth2_scheme)):
    return token


def upload_to_github(title, contents, filename, filecontents, label):
    # first upload file to swift
    swift.put_container(config.get('github', 'swift_container'))
    # Upload the object
    fileParts = os.path.splitext(filename)
    filename = f"{fileParts[0]}-{str(shortuuid.random())}{fileParts[1]}"
    e = swift.put_object(config.get('github', 'swift_container'), filename, filecontents)
    # public url
    file_url = os.path.join(config.get('github', 'swift_public_url'),filename)
    contents_with_file = f"{contents}\n <img alt='{filename}' src='{file_url}'>"
    labels = [label]
    issue = {
        'title': title,
        'body': contents_with_file,
        'labels': labels
    }
    data = {'issue': issue}
    headers = {
        'Authorization': f"token {config.get('github', 'github_token')}",
        'Accept': 'application/vnd.github.v3.html+json'
    }
    url = 'https://api.github.com/repos/%s/%s/issues' % (config.get('github', 'repo_owner'), config.get('github', 'repo_name'))
    response = requests.request('POST', url, data=json.dumps(issue), headers=headers)
    if response.status_code == 201:
        resp_obj = json.loads(response.content)
        return resp_obj.get('html_url')
    else:
        None




@router.post("/feedback")
async def send_feedback(title: str = Form(...), contents: str = Form(...), label: str = Form(...), 
                        uploadedFile: UploadFile = File(None), user: dict = Depends(keycloak.decode)):
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
            if config.get('github', 'enabled', default='false').strip() == 'true':
                github_issue_url = upload_to_github(title, contents, uploadedFile.filename, filecontents, label)
                if github_issue_url:
                    contents = f"{contents}<p />PS<br />"
                    contents = f"{contents}This feedback has been submitted as a <a href={github_issue_url}>github issue</a>"
            mail.send_mail_with_file(to_emails, title, contents, filecontents, uploadedFile.filename, ccemail=useremail)
        else:
            logger.info("No attachment present")
            if config.get('github', 'enabled', default='false').strip() == 'true':
                github_issue_url = await upload_to_github(title, contents, None, None)
                if github_issue_url:
                    contents = f"{contents}\n\nPS"
                    contents = f"{contents}This feedback has been submitted as a <a href={github_issue_url}>github issue</a>"
            mail.send_mail(to_emails, title, contents, subtype='plain', ccemail=useremail)
    except Exception as e:
        logger.error(f"Problem sending email: {str(e)}")
        raise