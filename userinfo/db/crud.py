import base64
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from . import models, schemas
from typing import List
import shortuuid, enum, datetime

import userinfo.mail as mail

import logging
logger = logging.getLogger('ippuserinfo')

class PermissionException(Exception):
    pass

class NotfoundException(Exception):
    pass

class AlreadyExistException(Exception):
    pass



############# file explorer #################
def get_filesexplorer(db: Session, filesexplorer_id: int):
    return db.query(models.FilesExplorer).filter(models.FilesExplorer.id == filesexplorer_id).first()

def get_filesexplorer_by_username_component(db: Session, username: str, component: str):
    return db.query(models.FilesExplorer).\
            filter(models.FilesExplorer.username == username, models.FilesExplorer.component == component).\
            first()

def get_filesexplorer_components(db: Session, username: str):
    return db.query(models.FilesExplorer.component.distinct()).\
            filter(models.FilesExplorer.username == username).\
            all()

def get_filesexplorers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FilesExplorer).offset(skip).limit(limit).all()

def create_filesexplorer(db: Session, filesxplorer: schemas.FilesExplorerBase):
    filesexplorer = models.FilesExplorer(
                                            username = filesxplorer.username,
                                            component = filesxplorer.component,
                                            currentpath = filesxplorer.currentpath,
                                            filters = filesxplorer.filters
                                        )
    db.add(filesexplorer)
    db.commit()
    db.refresh(filesexplorer)
    return filesexplorer

def update_filesexplorer(db: Session, filesxplorer_id: int, filesxplorer: schemas.FilesExplorerUpdate):
    """
    Update fileexplorer
    Append this to current path, delete one if exceed 10
    never update username, component
    """
    db_fileexplorer = get_filesexplorer(db, filesxplorer_id)
    # only update this, relaly
    db_fileexplorer.currentpath = filesxplorer.currentpath
    db_fileexplorer.filters = filesxplorer.filters
    # now modify lastpaths
    if not db_fileexplorer.currentpath in db_fileexplorer.lastpaths:
        db_fileexplorer.lastpaths = [db_fileexplorer.currentpath] + db_fileexplorer.lastpaths
        if len(db_fileexplorer.lastpaths) > 10:
            db_fileexplorer.lastpaths.pop()
    db.commit()
    db.refresh(db_fileexplorer)
    return db_fileexplorer


def get_bookmarks(db: Session, username: str, component: str, skip: int = 0, limit: int = 100):
    return db.query(models.Bookmark).offset(skip).limit(limit).all()


def create_bookmark(db: Session, filesexplorer_id: int, bookmark: schemas.BookmarkCreate):
    db_bookmark = models.Bookmark(**bookmark.dict(), filesexplorer_id=filesexplorer_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


def get_bookmark(db: Session, bookmark_id: int):
    return db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    
def delete_bookmark(db: Session, bookmark_id: int):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    if(bookmark):
        db.delete(bookmark)
        db.commit()

############# decon #################
def get_deconpage(db: Session, username: str):
    return db.query(models.DeconPage).\
            filter(models.DeconPage.username == username).\
            first()

def create_deconpage(db: Session, username: str):
    # check if exists
    db_deconpage = models.DeconPage(username = username)
    db.add(db_deconpage)
    db.commit()
    return db_deconpage
    
# add a new decon to a deconpage
# this assumes the seris is soready saved in the databsae
# a new setting will be created from series and default values
def create_decon_to_deconpage(db:Session, username: str, series_id: int):
    # get series first
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise NotfoundException('Not find the given series')
    # create a new Setting
    new_setting = models.Setting(**series.dict())
    db.add(new_setting)
    db.flush()
    # now create new decon
    new_decon = models.Decon(setting_id = new_setting.id,
                            series_id = series_id,
                            deconpage_id=username)
    db.add(new_decon)
    db.commit()
    db.refresh(new_decon)
    return new_decon
    
def create_decon_to_deconpage(db:Session, username: str, series_id: int, setting: schemas.SettingCreate):
    new_setting = models.Setting(**setting.dict())
    db.add(new_setting)
    db.flush()
    # now create new decon
    new_decon = models.Decon(setting_id = new_setting.id,
                            series_id = series_id,
                            deconpage_id=username)
    db.add(new_decon)
    db.commit()
    db.refresh(new_decon)
    return new_decon

def delete_decon(db: Session, decon: models.Decon):
    db.delete(decon)
    db.commit()
 
def delete_decon_from_path(db: Session, username: str, path: str):
    # a simple join
    decoded_path = base64.b64decode(path).decode("utf-8")
    for d, s in db.query(models.Decon, models.Series).\
                filter(models.Decon.series_id == models.Series.id).\
                filter(models.Decon.deconpage_id == username).\
                filter(models.Series.path == decoded_path).all():
        db.delete(d)
    db.commit()
    

def get_decons(db: Session, username: str, path: str):
    db_deconpage = get_deconpage(db, username)
    if not db_deconpage:
        db_deconpage = create_deconpage(db, username)
    decons = []
    if path:
        decoded_path = base64.b64decode(path).decode("utf-8")
        # print ("===============")
        # print (f"decoded path: {decoded_path}") 
        # a simple join
        for d, s in db.query(models.Decon, models.Series).\
                    filter(models.Decon.series_id == models.Series.id).\
                    filter(models.Decon.deconpage_id == username).\
                    filter(models.Series.path == decoded_path).all():
            decons.append(d)
        # print (len(decons))
    else:
        decons = db_deconpage.decons
    return decons
    
def get_decon_from_deconpage(db: Session, username: str, deconid: int):
    decon = db.query(models.Decon).\
                filter(models.Decon.id == deconid).\
                filter(models.Decon.deconpage_id == username).\
                first()
    return decon

def update_decon(db: Session, username: str, deconid: int, decon: schemas.DeconCreate, setting: schemas.SettingCreate):
    """
    Update decon - settings
    """
    # update decon
    existing_decon_dict = row2dict(get_decon_from_deconpage(db, username, deconid), True)
    stored_decon_model = schemas.Decon(**existing_decon_dict)
    update_decon_data = decon.dict(exclude_unset=True)
    updated_decon_item = stored_decon_model.copy(update=update_decon_data)
    updated_decon_item_dict = updated_decon_item.dict()
    updated_decon_item_dict.pop("jobs")
    # it does not like list of jobs as it is list of immutable dict
    db.query(models.Decon).filter(models.Decon.id == deconid).update(updated_decon_item_dict)
    # update setting
    setting_id = existing_decon_dict.get("setting_id")
    existing_setting = get_one_setting(db, setting_id)
    existing_setting_dict = row2dict(existing_setting)
    stored_setting_model = schemas.SettingCreate(**existing_setting_dict)
    update_setting_data = setting.dict(exclude_unset=True)
    updated_setting_item = stored_setting_model.copy(update=update_setting_data)
    db.query(models.Setting).filter(models.Setting.id == setting_id).update(updated_setting_item.dict())
    db.commit()


def row2dict(row, keep_id = False):
    d = {}
    for column in row.__table__.columns:
        if not keep_id and column.name == 'id':
            continue
        row_val = getattr(row, column.name)
        if isinstance(row_val, enum.Enum):
            row_val = row_val.value
        d[column.name] = row_val
    return d

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def create_decon_and_jobs(db:Session, username: str, email: str, decon_id: int, numberofjobs: int):
    """Create a new decon from the given decon_id, and create jobs with it"""
    decon = db.query(models.Decon).\
                filter(models.Decon.id == decon_id).\
                filter(models.Decon.deconpage_id == username).\
                first()
    if not decon:
        raise NotfoundException("Cannot find the given decon under this username")
    # create a new setting, reasons: existing setting can be changed
    # no need to create a new series, as it is always there
    existing_setting = db.query(models.Setting).\
                filter(models.Setting.id == decon.setting_id).\
                first()
    existing_setting_dict = row2dict(existing_setting)
    # print(existing_setting_dict)
    # print (object_as_dict(existing_setting))
    new_setting_schema = schemas.SettingBase(**existing_setting_dict)
    new_setting = models.Setting(**new_setting_schema.dict())
    db.add(new_setting)
    db.flush()
    # then create decon
    # create decon first
    db_decon = models.Decon(setting_id = new_setting.id,
                            series_id = decon.series_id)
    db.add(db_decon)
    db.flush()
    # create jobs accordinly
    created_jobs = []
    for i in range(numberofjobs):
        db_job = models.Job(id=shortuuid.uuid(), username = username, 
                            email=email, decon_id = db_decon.id)
        db.add(db_job)
        db.flush()
        db.refresh(db_job)
        created_jobs.append(db_job)
    db.commit()
    return created_jobs

## series
def get_all_series(db: Session):
    return db.query(models.Series).all()

def get_one_series(db: Session, serie_id: int):
    return db.query(models.Series).filter(models.Series.id == serie_id).first()

def get_one_series_by_path(db: Session, path: str):
    return db.query(models.Series).filter(models.Series.path == path).all()

def create_series(db: Session, series: schemas.SeriesCreate):
    stored_serie = get_one_series_by_path(db, series.path)
    if stored_serie:
        raise AlreadyExistException('Series with given path already exists')
    db_serie = models.Series(**series.dict())
    db.add(db_serie)
    # print ("adding series")
    db.commit()
    db.refresh(db_serie)
    # print (db_serie)
    return db_serie

## settings
def get_all_settings(db: Session):
    return db.query(models.Setting).all()

def get_one_setting(db: Session, setting_id: int):
    return db.query(models.Setting).filter(models.Setting.id == setting_id).first()

def update_setting(db: Session, username: str, setting_id: int, setting: schemas.SettingCreate):
    existing_setting = get_one_setting(db, setting_id)
    existing_setting_dict = row2dict(existing_setting)
    stored_item_model = schemas.SettingCreate(**existing_setting_dict)
    update_data = setting.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    db.query(models.Setting).filter(models.Setting.id == setting_id).update(updated_item.dict())
    db.commit()



############# templates #################
def get_templates(db:Session, username: str):
    return db.query(models.Template).\
            filter(models.Template.username == username).\
            all()

def create_template(db: Session, username: str, setting: schemas.SettingCreate, templatename: str):
    # create setting
    db_setting = models.Setting(**setting.dict())
    db.add(db_setting)
    db.flush()
    # create template name
    db_template = models.Template(username=username, 
                                    name=templatename,
                                    setting_id=db_setting.id)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def get_template(db: Session, username: str, templateid: int):
    return db.query(models.Template).\
            filter(models.Template.username == username).\
            filter(models.Template.id == templateid).\
            first()

def delete_template(db: Session, template: models.Template):
    template = db.query(models.Template).\
                filter(models.Template.username == username).\
                filter(models.Template.id == templateid).\
                first()
    db.delete(template)
    db.commit()


############# jobs #################
def get_jobs(db:Session, username: str, all):
    if all:
        return db.query(models.Job).\
            filter(models.Job.username == username).\
            all()
    else:
        # return non FAILED, COMPLETED job
        return db.query(models.Job).\
            filter(models.Job.username == username).\
            filter(models.Job.status.notin_(['FAILED', 'COMPLETE'])).\
            all()

def get_job(db:Session, jobid: str):
    return db.query(models.Job).\
            filter(models.Job.id == jobid).\
            first()

def create_email_contents(finished_jobs, series, setting):
    """
    Create html contents of the emails
    """
    contents = f"""
    <html>
        <head></head>
        <body>
            <p>Dear Image Processing Portal user!<br />

            <p>The { 'series' if series.isfolder else 'file' } <b>{ series.path }</b> has been processed! <p/>
            
            <p>The following jobs are created: <br />
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <th style="border: 1px solid black;">Job ID</th>
                    <th style="border: 1px solid black;">Job name</th>
                    <th style="border: 1px solid black;">Start</th> 
                    <th style="border: 1px solid black;">Finish</th>
                    <th style="border: 1px solid black;">Total files</th>
                    <th style="border: 1px solid black;">Success</th>
                    <th style="border: 1px solid black;">Fail</th>
                </tr>
            """
    for job in finished_jobs:
        contents = contents + f"""
                                <tr>
                                    <td style="border: 1px solid black;"> {job.jobid} </td>
                                    <td style="border: 1px solid black;"> {job.jobname} </td>
                                    <td style="border: 1px solid black;"> {job.start} </td>
                                    <td style="border: 1px solid black;"> {job.end} </td>
                                    <td style="border: 1px solid black;"> {job.total} </td>
                                    <td style="border: 1px solid black;"> {job.success} </td>
                                    <td style="border: 1px solid black;"> {job.fail} </td>
                                </tr>
                                """
    contents = f"{contents}</table> <p/><p/>"
    # now list the settings fields
    contents = f"""{contents} The following parameters are used for these jobs:<br/>
                    <table style="width:100%; border-collapse:collapse;">
                    <tr>
                        <th style="border: 1px solid black;">Parameter</th>
                        <th style="border: 1px solid black;">value</th>
                    </tr>
                """
    setting_dict = row2dict(setting)
    for param in setting_dict:
        # not interested in id
        if "id" in param:
            continue
        else:
            contents = contents + f"""
                                <tr>
                                    <td style="border: 1px solid black;"> {param} </td>
                                    <td style="border: 1px solid black;"> {setting_dict.get(param)} </td>
                                </tr>"""
    contents = f"{contents}</table> <p/><p/>"

    contents = f"{contents} Best Regards,"
    return contents

def update_job(db:Session, jobid: str, job: schemas.JobCreate):
    existing_job = get_job(db, jobid)
    existing_job_dict = row2dict(existing_job)
    stored_item_model = schemas.JobCreate(**existing_job_dict)
    update_data = job.dict(exclude_unset=True)
    if update_data.get('status') in ('FAILED', 'COMPLETE'):
        update_data['end'] = datetime.datetime.utcnow()
    updated_item = stored_item_model.copy(update=update_data)
    db.query(models.Job).\
        filter(models.Job.id == jobid).\
        update(updated_item.dict())
    db.commit()
    # check if the job stat is FAIL or COMPLETE
    if 'status' in update_data.keys():
        new_job_stat = update_data.get('status')
        # get decon_id from existing job
        decon_id = existing_job_dict.get('decon_id')
        if new_job_stat in ('FAILED', 'COMPLETE'):
            total_jobs = db.query(models.Job).filter(models.Job.decon_id == decon_id).all()
            # meaning a new job is done/or failed
            finished_jobs = db.query(models.Job).\
                filter(models.Job.decon_id == decon_id).\
                filter(models.Job.status.in_(['FAILED', 'COMPLETE'])).\
                all()
            logger.debug("Total jobs = %d, finished jobs = %d" %(len(total_jobs), len(finished_jobs)))
            if len(total_jobs) == len(finished_jobs):
                # get settings and series
                decon = db.query(models.Decon).filter(models.Decon.id == decon_id).first()
                series = db.query(models.Series).filter(models.Series.id == decon.series_id).first()
                setting = db.query(models.Setting).filter(models.Setting.id == decon.setting_id).first()
                logger.debug("Sending user email to %s" %(existing_job_dict.get('email')))
                # send email
                if series.isfolder:
                    subject = 'Your series have been processed!'
                else:
                    subject = 'Your files have been processed!'
                contents = create_email_contents(finished_jobs, series, setting)
                mail.send_mail(existing_job_dict.get('email'), subject, contents)


def delete_job(db:Session, username: str, jobid: str):
    job = db.query(models.Job).\
        filter(models.Job.username == username).\
        filter(models.Job.id == jobid).first()
    # get decon with job
    decon = db.query(models.Decon).\
        filter(models.Decon.id == job.decon_id).first()
    db.delete(job)
    db.delete(decon)
    db.commit()


def delete_jobs(db:Session, username: str, jobs: List[str]):
    # query
    jobslist = db.query(models.Job).\
        filter(models.Job.username == username).\
        filter(models.Job.id.in_(jobs)).all()
    # get decons ids
    decon_ids = []
    for job in jobslist:
        decon_ids.append(job.decon_id)
    # delete all jobs given
    db.query(models.Job).\
        filter(models.Job.username == username).\
        filter(models.Job.id.in_(jobs)).delete(synchronize_session=False)
    db.query(models.Decon).\
        filter(models.Decon.id.in_(decon_ids)).delete(synchronize_session=False)
    db.commit()