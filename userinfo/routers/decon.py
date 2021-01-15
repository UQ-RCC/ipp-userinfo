from fastapi import APIRouter, Response, Depends, HTTPException
import userinfo.db as udb
import userinfo.keycloak as keycloak
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
router = APIRouter()

@router.get("/deconpage", response_model=udb.schemas.DeconPage)
def get_deconpage(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    deconpage = udb.crud.get_deconpage(db, username)
    # create one if not there
    if not deconpage:
        deconpage = udb.crud.create_deconpage(db, username)
    return deconpage


@router.get("/deconpage/decons", response_model=List[udb.schemas.Decon])
def get_decons_in_page(user: dict = Depends(keycloak.decode), 
                        db: Session = Depends(udb.get_db),
                        path: Optional[str] = None):
    username = user.get('preferred_username')
    return udb.crud.get_decons(db, username, path)
    
@router.post("/deconpage/decons", response_model=udb.schemas.Decon)
def create_decon(series_id: int,
                setting: udb.schemas.SettingCreate,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    db_decon = udb.crud.create_decon_to_deconpage(db, username, series_id, setting)
    return db_decon

@router.get("/deconpage/decons/{deconid}", response_model=udb.schemas.Decon)
def get_decon(  deconid: int,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    db_decon = udb.crud.get_decon_from_deconpage(db, username, deconid)
    return db_decon


@router.delete("/deconpage/decons")
def delete_decon_using_path(user: dict = Depends(keycloak.decode), 
                        db: Session = Depends(udb.get_db),
                        path: Optional[str] = None):
    username = user.get('preferred_username')
    return udb.crud.delete_decon_from_path(db, username, path)


@router.delete("/deconpage/decons/{deconid}")
def delete_decon(
                deconid: int,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    db_decon = udb.crud.get_decon_from_deconpage(db, username, deconid)
    if not db_decon:
        udb.crud.delete_decon(db, db_decon)
    else:
        return HTTPException(status_code=400, detail=f"Either no decon with {deconid} or not belong to this user")


##### series
@router.get("/series", response_model=List[udb.schemas.Series])
def get_series(db: Session = Depends(udb.get_db), path: Optional[str] = None):
    """returns all series"""
    if path:
        decoded_path = base64.b64decode(path).decode("utf-8") 
        # path is in base64
        return udb.crud.get_one_series_by_path(db, decoded_path)
    else:
        return udb.crud.get_all_series(db)
        

@router.get("/series/{serieid}", response_model=udb.schemas.Series)
def get_a_series(serieid: int, db: Session = Depends(udb.get_db)):
    """returns a specific series"""
    return udb.crud.get_one_series(db, serieid)
    
@router.post("/series")
def create_series(
                series: udb.schemas.SeriesCreate,
                user: dict = Depends(keycloak.decode),
                db: Session = Depends(udb.get_db)):
    """update a specific series"""
    username = user.get('preferred_username')
    try:
        return udb.crud.create_series(db, series)
    except udb.crud.AlreadyExistException as e:
        return HTTPException(status_code=304, detail=f"Series with given path already exists")
    except Exception as e:
        return HTTPException(status_code=400, detail=f"Error: {e}")
    

##### setting
@router.get("/settings", response_model=List[udb.schemas.Setting])
def get_settings(db: Session = Depends(udb.get_db)):
    """returns all settings"""
    return udb.crud.get_all_settings(db)

@router.get("/settings/{settingid}", response_model=udb.schemas.Setting)
def get_setting(settingid: int, db: Session = Depends(udb.get_db)):
    """update series"""
    return udb.crud.get_one_setting(db, settingid)

@router.put("/settings/{settingid}")
def update_settings(
                    settingid: int, setting: udb.schemas.SettingCreate,
                    user: dict = Depends(keycloak.decode),
                    db: Session = Depends(udb.get_db)):
    """update series"""
    username = user.get('preferred_username')
    stored_setting = udb.crud.get_one_setting(db, settingid)
    if not stored_setting:
        return HTTPException(status_code=400, detail=f"Could not find the setting with id: {settindid}")
    if not stored_setting.decon or stored_setting.decon.deconpage_id != username:
        return HTTPException(status_code=400, detail=f"Setting with id: {settingid} does not belong to user: {username}")
    udb.crud.update_setting(db, username, settingid, setting)
        


######## templates
@router.get("/templates", response_model=List[udb.schemas.Template])
def get_templates(user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.get_templates(db, username)

@router.post("/templates", response_model=udb.schemas.Template)
def create_template(
                templatename: str,
                setting: udb.schemas.SettingCreate,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.create_template(db, username, setting, templatename)

@router.get("/templates/{templateid}", response_model=udb.schemas.Setting)
def get_template(templateid: int,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    template = udb.crud.get_template(db, username, templateid)
    if template:
        return udb.crud.get_one_setting(db, template.setting_id)
    else:
        return HTTPException(status_code=400, detail=f"Ether template is empty or not found")
        

@router.delete("/templates/{templateid}")
def delete_template(templateid: int,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    template = udb.crud.get_template(db, username, templateid)
    if not template:
        return HTTPException(status_code=404, detail=f"Not found template with id: {templateid}")
    udb.crud.delete_template(db, template)

######## job
@router.get("/jobs", response_model=List[udb.schemas.Job])
def get_jobs(user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    return udb.crud.get_jobs(db, username)



@router.post("/jobs", response_model=List[udb.schemas.Job])
def create_jobs(
                decon_id: int, 
                numberofjobs: int,
                user: dict = Depends(keycloak.decode), 
                db: Session = Depends(udb.get_db)):
    """create jobs"""
    username = user.get('preferred_username')
    try:
        return udb.crud.create_decon_and_jobs(db, username, decon_id, numberofjobs)
    except udb.crud.NotfoundException:
        return HTTPException(status_code=404, detail=f"Not found decon with id: {decon_id}")




