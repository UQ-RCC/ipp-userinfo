import base64
from sqlalchemy.orm import Session
from sqlalchemy import inspect, func
from urllib.parse import quote
from . import models, schemas
from typing import List
import shortuuid, enum, datetime

import time

import userinfo.mail as mail
import userinfo.config as config
import logging
import pytz
logger = logging.getLogger('ippuserinfo')


class PermissionException(Exception):
    pass

class NotfoundException(Exception):
    pass

class AlreadyExistException(Exception):
    pass

class CannotChangeException(Exception):
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
    db.flush()
    # db.refresh(filesexplorer)
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
    db.flush()
    # db.refresh(db_fileexplorer)
    return db_fileexplorer


def get_bookmarks(db: Session, username: str, component: str, skip: int = 0, limit: int = 100):
    return db.query(models.Bookmark).offset(skip).limit(limit).all()


def create_bookmark(db: Session, filesexplorer_id: int, bookmark: schemas.BookmarkCreate):
    db_bookmark = models.Bookmark(**bookmark.dict(), filesexplorer_id=filesexplorer_id)
    db.add(db_bookmark)
    db.commit()
    db.flush()
    # db.refresh(db_bookmark)
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
    db.flush()
    # db.refresh(new_decon)
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
    db.flush()
    # db.refresh(new_decon)
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
    

def get_decons(db: Session, username: str, api:str, path: str):
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
                    filter(models.Series.path == decoded_path).\
                    filter(models.Decon.api == api).all():
            decons.append(d)
        # print (len(decons))
    else:
        #decons = db_deconpage.decons
        api = base64.b64decode(api).decode("utf-8")
        for d, s in db.query(models.Decon, models.DeconPage).\
                    filter(models.Decon.deconpage_id == models.DeconPage.username ).\
                    filter(models.Decon.deconpage_id == username ).\
                    filter(models.Decon.api == api).all():
            decons.append(d)
        logger.debug(f"update: {decons}", exc_info=True)
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
        # db.refresh(db_job)
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
    db.commit()
    db.flush()
    db.refresh(db_serie)
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
    logger.debug(f"New settings: {setting}")
    db_setting = models.Setting(**setting.dict())
    db.add(db_setting)
    db.flush()
    # create template name
    db_template = models.Template(username=username, 
                                    name=templatename,
                                    setting_id=db_setting.id)
    db.add(db_template)
    db.commit()
    db.flush()
    # db.refresh(db_template)
    return db_template


def get_template(db: Session, username: str, templateid: int):
    return db.query(models.Template).\
            filter(models.Template.username == username).\
            filter(models.Template.id == templateid).\
            first()

def delete_template(db: Session, template: models.Template):
    db.delete(template)
    db.commit()

#############pinhole calculator settings #########
def get_pincal_settings(db:Session, username: str, illuminationType:str):
    logger.info(f"get settings list ",exc_info=True)

    q = db.query(models.PcalSetting).\
            filter(models.PcalSetting.username == username).\
                filter(models.PcalSetting.illuminationtype == illuminationType)
    
    logger.info(f"get settings list queary :{q} ",exc_info=True)
    return q.all()
            

def create_setting_file(db: Session, setting: schemas.PcalSettingCreate, username: str):
    # create setting
    logger.debug(f"Add new pinhole calculator settings: {setting}")
    db_setting = models.PcalSetting(**setting.dict())
    db.add(db_setting)
    logger.debug(f"Add new record: {db_setting}", exc_info=True)
    db.commit()
    db.flush()
    return db_setting

def update_setting_file (db: Session, existing_file_record: models.PcalSetting, username: str, file_name:str, setting: schemas.PcalSettingCreate):
    logger.debug(f"Update pinhole calculator settings: {existing_file_record}")
    existing_file_record_dict = row2dict(existing_file_record)
    stored_item_model = schemas.PcalSettingCreate(**existing_file_record_dict)
    update_data = setting.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    logger.debug(f"Update existing record with new data: {updated_item}", exc_info=True)
    db.query(models.PcalSetting).filter(models.PcalSetting.username == username).filter(models.PcalSetting.name == file_name).update(updated_item.dict())
    db.commit()


def get_pincal_setting_file(db: Session, settingid: int):
    return db.query(models.PcalSetting).\
            filter(models.PcalSetting.id == settingid).\
            first()

def delete_pincal_setting_file(db: Session, setting: models.PcalSetting):
    db.delete(setting)
    db.commit()

def get_record_by_name(db: Session, username: str, name: str):
    return db.query(models.PcalSetting).\
            filter(models.PcalSetting.username == username).\
            filter(models.PcalSetting.name == name).\
            first()


############# jobs #################
def get_jobs(db:Session, username: str, all):
    if all:
        return db.query(models.Job).\
            filter(models.Job.username == username).\
            all()
    else:
        # return non FAILED, COMPLETED, CANCELLED job
        return db.query(models.Job).\
            filter(models.Job.username == username).\
            filter(models.Job.status.notin_(['FAILED', 'COMPLETE', 'CANCELLED'])).\
            all()

def filter_jobs(db: Session, status: str, username: str, start: datetime.date, jobname: str):
    q = db.query(models.Job)
    if status:
        q = q.filter(models.Job.status == status)
    if username:
        q = q.filter(models.Job.username == username)
    if jobname:
        q = q.filter(models.Job.jobname == jobname)
    if start:
        q = q.filter(func.date(models.Job.start) >= start)
    return q.all()
    
    


def get_job(db:Session, jobid: str):
    return db.query(models.Job).\
            filter(models.Job.id == jobid).\
            first()




def create_decon_email_contents(finished_jobs, series, setting,job_status):
    """
    Create html contents of the emails
    """
    logger.debug(f"decon email setings: {setting}")
    setting_dict = row2dict(setting)
    _job_output_path = setting.outputPath
    if not _job_output_path:
        _job_output_path = "/"
    if not _job_output_path.endswith('/'):
        _job_output_path = _job_output_path + '/'
    logger.debug(f"clinet uri:{config.get('client', 'uri')}")
    logger.info(f"Email details: {quote(_job_output_path)}")
    output_access_url = config.get('client', 'uri') + '?component=filesmanager&path=' + quote(_job_output_path)
    logger.info(f"Email details: {output_access_url}")
    
    contents = f"""
    <html>
        <head></head>
        <body>
            <p>Dear Image Processing Portal user!<br />
            
            <p>The { 'series' if series.isfolder else 'file' } <b>{ series.path }</b> has been { 'failed!' if job_status=='FAILED' else 'processed!' }  <p/>
            <p>You can access the output <a href="{output_access_url}">here</a></p>
            <p>The following jobs were created: <br />
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <th style="border: 1px solid black;">Job#</th>
                    <th style="border: 1px solid black;">Slurm Job#</th>
                    <th style="border: 1px solid black;">Name</th>
                    <th style="border: 1px solid black;">Submitted</th>
                    <th style="border: 1px solid black;">Start</th> 
                    <th style="border: 1px solid black;">Finish</th>
                    <th style="border: 1px solid black;">Total files</th>
                    <th style="border: 1px solid black;">Success</th>
                    <th style="border: 1px solid black;">Fail</th>
                </tr>
            """
    for job in finished_jobs:
        local_submitted_time = (job.submitted).astimezone(pytz.timezone('Australia/Brisbane'))
    
        contents = contents + f"""
                                <tr>
                                    <td style="border: 1px solid black;"> {job.id} </td>
                                    <td style="border: 1px solid black;"> {job.jobid} </td>
                                    <td style="border: 1px solid black;"> {job.jobname} </td>
                                    <td style="border: 1px solid black;"> {local_submitted_time} </td>
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

def create_convert_email_contents(existing_job_dict, convert, new_job_status):
    """
    Create html contents of the emails
    """
    if not convert.outputPath:
        convert.outputPath = "/"
    if not convert.outputPath.endswith('/'):
        convert.outputPath = convert.outputPath + '/'
    output_access_url = config.get('client', 'uri') + '?component=filesmanager&path=' + quote(convert.outputPath)
    contents = f"""
    <html>
        <head></head>
        <body>
            <p>Dear Image Processing Portal user!<br />
            Your recent conversion job has finished. <br />
            Job information:<br />
            <ul> 
            <li>Job status: {new_job_status} </li>
            <li>System job id: {existing_job_dict.get('id')} </li>
            <li>Slurm job id : {existing_job_dict.get('jobid')} </li>
            <li>Output folder: <a href="{output_access_url}">{convert.outputPath}</a></li> <br />
            
            <p> The following files/series were processed: <br />
            <ul>"""
    for inputPath in convert.inputPaths:
        contents = f"{contents}<li>{inputPath}</li>"
    contents = f"{contents}</ul><br />"
    contents = f"{contents} Best Regards,"
    return contents

def create_preprocessing_email_contents(existing_job_dict, preprocessing, psettings, new_job_status):
    if not preprocessing.outputPath:
        preprocessing.outputPath = "/"
    if not preprocessing.outputPath.endswith('/'):
        preprocessing.outputPath = preprocessing.outputPath + '/'
    output_access_url = config.get('client', 'uri') + '?component=filesmanager&path=' + quote(preprocessing.outputPath)
    contents = f"""
    <html>
        <head></head>
        <body>
            <p>Dear Image Processing Portal user!<br />
            Your recent preprocessing job has finished. <br />
            Job information:<br />
            <ul>
            <li>Job status: {new_job_status} </li> 
            <li>System job id: {existing_job_dict.get('id')} </li>
            <li>Slurm job id : {existing_job_dict.get('jobid')} </li>
            <li>Output folder: <a href="{output_access_url}">{preprocessing.outputPath}</a></li> <br />
            
            <p> The following files/series were processed: <br />
            """
    for psetting in psettings:
        contents = f"""{contents} <b> {psetting.path} </b><br />"""
        contents = f"""{contents}
                    <table style="width:100%; border-collapse:collapse;">
                    <tr>
                        <th style="border: 1px solid black;">Parameter</th>
                        <th style="border: 1px solid black;">value</th>
                    </tr>
                """
        psetting_dict = row2dict(psetting)
        for param in psetting_dict:
            # not interested in id and path (already displayed)
            if "id" in param or "path" in param:
                continue
            else:
                contents = contents + f"""
                                    <tr>
                                        <td style="border: 1px solid black;"> {param} </td>
                                        <td style="border: 1px solid black;"> {psetting_dict.get(param)} </td>
                                    </tr>"""
        contents = f"{contents}</table><p/>"

    contents = f"{contents} <p/> <p/>Best Regards,"
    return contents

def create_macro_email_contents(existing_job_dict, macro, new_job_status):
    """
    Create html contents of the emails
    """
    if not macro.outputPath:
        macro.outputPath = "/"
    if not macro.outputPath.endswith('/'):
        macro.outputPath = macro.outputPath + '/'
    output_access_url = config.get('client', 'uri') + '?component=filesmanager&path=' + quote(macro.outputPath)
    contents = f"""
    <html>
        <head></head>
        <body>
            <p>Dear Image Processing Portal user!<br />
            Your recent macro job has finished. <br />
            Job information:<br />
            <ul> 
            <li>Job status: {new_job_status} </li>
            <li>System job id: {existing_job_dict.get('id')} </li>
            <li>Slurm job id : {existing_job_dict.get('jobid')} </li>
            <li>Output folder: <a href="{output_access_url}">{macro.outputPath}</a></li> <br />
            
            <p> The following files/series were processed: <br />
            <ul>"""
    for inputPath in macro.inputPaths:
        contents = f"{contents}<li>{inputPath}</li>"
    contents = f"{contents}</ul><br />"
    contents = f"{contents} Best Regards,"
    return contents


def update_job(db:Session, jobid: str, job: schemas.JobCreate):
    logger.debug(f"Updating jobid: {jobid}")
    existing_job = get_job(db, jobid)
    existing_job_dict = row2dict(existing_job, True)
    logger.debug(existing_job_dict)
    stored_item_model = schemas.JobCreate(**existing_job_dict)
    # if existing_job is failed, complete then return
    if stored_item_model.status in ('FAILED', 'COMPLETE'):
        logger.debug("Job status cannot be changed once in FAILED or COMPLETE")
        raise CannotChangeException('Cannot changed terminated job')        
    update_data = job.dict(exclude_unset=True)
    if update_data.get('status') in ('FAILED', 'COMPLETE'):
        if update_data.get('end') is None:
            update_data['end'] = datetime.datetime.utcnow()
        
    updated_item = stored_item_model.copy(update=update_data)
    db.query(models.Job).\
        filter(models.Job.id == jobid).\
        update(updated_item.dict())
    db.flush()
    db.commit()
    # check if the job stat is FAIL or COMPLETE
    if 'status' in update_data.keys():
        logger.debug(f"Updating job with status: {update_data.get('status')}")
        new_job_stat = update_data.get('status')
        # get decon_id from existing job
        if new_job_stat in ('FAILED', 'COMPLETE'):
            decon_id = existing_job_dict.get('decon_id')
            preprocessing_id = existing_job_dict.get('preprocessing_id')
            convert_id = existing_job_dict.get('convert_id')
            macro_id = existing_job_dict.get('macro_id')
            sendEmail = existing_job_dict.get('sendemail')
            email = existing_job_dict.get('email')
            subject = contents = ''
            logger.info(f"Send Email details: {sendEmail}")
            logger.info(f"Email details: {email}")

            ######## decon job
            if not preprocessing_id and not convert_id and not macro_id and decon_id: 
                logger.debug(f"decon job, deconid={decon_id}")
                total_jobs = db.query(models.Job).filter(models.Job.decon_id == decon_id).all()
                # meaning a new job is done/or failed
                finished_jobs = db.query(models.Job).\
                    filter(models.Job.decon_id == decon_id).\
                    filter(models.Job.status.in_(['FAILED', 'COMPLETE'])).\
                    all()
                logger.debug(f"Total jobs = {len(total_jobs)}, finished jobs = {len(finished_jobs)}")
                # logger.debug(total_jobs)
                # logger.debug(finished_jobs)
                if len(total_jobs) == len(finished_jobs) and sendEmail:
                    # get settings and series
                    decon = db.query(models.Decon).filter(models.Decon.id == decon_id).first()
                    series = db.query(models.Series).filter(models.Series.id == decon.series_id).first()
                    setting = db.query(models.Setting).filter(models.Setting.id == decon.setting_id).first()
                    logger.debug(f"Sending user email to {existing_job_dict.get('email')}")
                    # send email
                    if (new_job_stat == 'FAILED'):
                        subject = 'Your decon jobs have failed!'
                    else:
                        subject = 'Your decon jobs have finished!'
                    contents = create_decon_email_contents(finished_jobs, series, setting, new_job_stat)
                else:
                    sendEmail = False
            #### convert job
            elif not preprocessing_id and convert_id and not decon_id and not macro_id:
                logger.debug(f"Convert job, convertid={convert_id}")
                if sendEmail:
                    convert = db.query(models.Convert).filter(models.Convert.id == convert_id).first()
                    #subject = 'Your conversion job has finished!'
                    if (new_job_stat == 'FAILED'):
                        subject = 'Your conversion job have failed!'
                    else:
                        subject = 'Your conversion job has finished!'
                    contents = create_convert_email_contents(existing_job_dict, convert, new_job_stat)
            #### preprocess job
            elif preprocessing_id and not convert_id and not decon_id and not macro_id:
                logger.debug(f"Preprocessing job - preprocessingid={preprocessing_id}")
                if sendEmail:
                    preprocessing = db.query(models.Preprocessing).filter(models.Preprocessing.id == preprocessing_id).first()
                    # get psettings
                    psettings = db.query(models.PSetting).filter(models.PSetting.preprocessing_id == preprocessing_id).all()
                    for psetting in psettings:
                        _serie = db.query(models.Series).filter(models.Series.id == psetting.series_id).first()
                        psetting.path = _serie.path
                    #subject = 'Your preprocessing job has finished!'
                    if (new_job_stat == 'FAILED'):
                        subject = 'Your preprocessing job have failed!'
                    else:
                        subject = 'Your preprocessing job has finished!'
                    contents = create_preprocessing_email_contents(existing_job_dict, preprocessing, psettings, new_job_stat)
            #### macro job
            elif macro_id and not preprocessing_id and not convert_id and not decon_id:
                logger.debug(f"Macro job, macro_id={macro_id}")
                if sendEmail:
                    macro = db.query(models.Macro).filter(models.Macro.id == macro_id).first()
                    #subject = 'Your macro job has finished!'
                    if (new_job_stat == 'FAILED'):
                        subject = 'Your macro job have failed!'
                    else:
                        subject = 'Your macro job has finished!'
                    contents = create_macro_email_contents(existing_job_dict, macro, new_job_stat)
            if sendEmail:
                try:
                    mail.send_mail(email, subject, contents)
                except Exception as e:
                    logger.error(f"Problem sending email: {str(e)}", exc_info=True)
                    raise
                


def delete_job(db:Session, username: str, jobid: str):
    job = db.query(models.Job).\
        filter(models.Job.username == username).\
        filter(models.Job.id == jobid).first()
    # get decon with job
    # decon = db.query(models.Decon).\
    #     filter(models.Decon.id == job.decon_id).first()
    if job:
        logger.debug(f"Deleting job with id={jobid}")
        db.delete(job)
        db.commit()
    else:
        logger.debug(f"Job with id={jobid} does not exist")
        
    


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


#### convert page
def get_convertpage(db: Session, username: str):
    return db.query(models.ConvertPage).\
            filter(models.ConvertPage.username == username).\
            first()


def create_convertpage(db: Session, username: str):
    convertpage = models.ConvertPage(username = username)
    db.add(convertpage)
    db.flush()
    convert = models.Convert(convertpage_id = username, convertpage=convertpage)
    db.add(convert)
    db.commit()
    db.flush()
    db.refresh(convertpage)
    return convertpage

def create_new_convert(db: Session, username: str):
    # first get convertpage
    convertpage = get_convertpage(db, username)
    # get the preprocessing
    if convertpage.convert:
        convertpage.convert.convertpage_id = None
        convert = models.Convert(convertpage_id = username, convertpage=convertpage, 
                                outputPath=convertpage.convert.outputPath, prefix=convertpage.convert.prefix,
                                method=convertpage.convert.method,inputPaths=convertpage.convert.inputPaths,
                                maxsize=convertpage.convert.maxsize)
    else:
        convert = models.Convert(convertpage_id = username, convertpage=convertpage)
        
    db.add(convert)
    db.flush()
    db.commit()
    db.refresh(convert)
    return convert
    
def get_convert(db: Session, username: str, convertid: int):
    return db.query(models.Convert).\
            filter(models.Convert.id == convertid).\
            first()

def update_convert(db: Session, username: str, convertid:int, convert: schemas.ConvertCreate):
    db_convert = get_convert(db, username, convertid)
    # update
    db_convert.outputPath = convert.outputPath
    db_convert.prefix = convert.prefix
    db_convert.method = convert.method
    db_convert.inputPaths = convert.inputPaths
    db_convert.maxsize = convert.maxsize
    db.commit()
    db.flush()
    db.refresh(db_convert)
    return db_convert

def get_convert_job(db: Session, username: str, email: str, convertid:int, sendemail: bool):
    convert = get_convert(db, username, convertid)
    if not convert: 
        raise NotfoundException(f"Cannot find convert with id={convertid}")
    job = db.query(models.Job).\
            filter(models.Job.convert_id == convertid).\
            filter(models.Job.decon_id == None).\
            filter(models.Job.preprocessing_id == None ).\
            filter(models.Job.macro_id == None).\
            first()
    if not job:
        job = models.Job(id=shortuuid.uuid(), username=username, email=email, decon_id=None, convert_id=convertid, preprocessing_id=None, macro_id=None, sendemail=sendemail)
        db.add(job)
        db.flush()
        db.commit()
    return job


def create_convert_job(db: Session, username: str, email: str, sendEmail: bool):
    db_job = models.Job(id=shortuuid.uuid(), username = username, 
                    email=email, convertpage_username = username,
                    sendemail=sendEmail)
    db.add(db_job)
    db.commit()
    db.flush()
    db.refresh(db_job)
    return db_job


#### preprocess page
def get_preprocessingpage(db: Session, username: str):
    return db.query(models.PreprocessingPage).\
            filter(models.PreprocessingPage.username == username).\
            first()

# also create an empty processing 
def create_preprocessingpage(db: Session, username: str):
    preprocessingpage = models.PreprocessingPage(username = username)
    preprocessing = models.Preprocessing(preprocessingpage_id = username, preprocessingpage=preprocessingpage, psettings=[])
    db.add(preprocessing)
    db.flush()
    preprocessingpage.preprocessing = preprocessing
    db.add(preprocessingpage)
    db.flush()
    db.commit()
    return preprocessingpage

# create new processing with same psettings as current ones 
def create_new_processing(db: Session, username: str):
    # first get preprocessingpage
    preprocessingpage = get_preprocessingpage(db, username)
    # get the preprocessing
    psettings = []
    outputPath = ""
    combine = False
    if preprocessingpage.preprocessing:
        psettings = preprocessingpage.preprocessing.psettings
        preprocessingpage.preprocessing.preprocessingpage_id = None
        combine = preprocessingpage.preprocessing.combine
        outputPath = preprocessingpage.preprocessing.outputPath
    preprocessing = models.Preprocessing(preprocessingpage_id = username, 
                                        preprocessingpage=preprocessingpage,
                                        outputPath=outputPath,
                                        combine=combine)
    db.add(preprocessing)
    db.flush()
    newpsettings = []
    for psetting in psettings:
        _newpsetting = models.PSetting(deskew=psetting.deskew, keepDeskew=psetting.keepDeskew,
                                        background=psetting.background, stddev=psetting.stddev,
                                        unit=psetting.unit, pixelWidth=psetting.pixelWidth,
                                        pixelHeight=psetting.pixelHeight, pixelDepth=psetting.pixelDepth, 
                                        angle=psetting.angle, threshold=psetting.threshold,
                                        centerAndAverage=psetting.centerAndAverage, order=psetting.order,
                                        series_id=psetting.series_id, preprocessing_id=preprocessing.id)
        db.add(_newpsetting)
        db.flush()
        newpsettings.append(_newpsetting)
    preprocessing.psettings = newpsettings
    db.flush()
    db.commit()
    db.refresh(preprocessing)
    return preprocessing


    

# get a preprocessing
def get_a_processing(db: Session, username: str, preprocessingid: int):
    return db.query(models.Preprocessing).\
            filter(models.Preprocessing.id == preprocessingid).\
            first()

def get_processing_job(db: Session, username: str, email: str, preprocessingid: int, sendemail: bool):
    preprocessing = get_a_processing(db, username, preprocessingid)
    if not preprocessing: 
        raise NotfoundException(f"Cannot find preprocessing with id={preprocessingid}")
    
    job = db.query(models.Job).\
            filter(models.Job.preprocessing_id == preprocessingid).\
            filter(models.Job.decon_id == None).\
            filter(models.Job.convert_id == None).\
            filter(models.Job.macro_id == None).\
            first()
    if not job:
        logger.debug("Create new processing job:")
        job = models.Job(id=shortuuid.uuid(), username=username, email=email, 
                        decon_id=None, convert_id=None, preprocessing_id=preprocessing.id, 
                        macro_id=None, sendemail=sendemail)
        db.add(job)
        db.flush()
        db.commit()
        logger.debug(job)
    return job


def create_new_psetting(db: Session, username: str, preprocessingid: int, seriesid: int):
    # get series
    serie = get_one_series(db, seriesid)
    if not serie:
        raise NotfoundException(f"Cannot find series with id={seriesid}")
    # get preprocessing
    preprocessing = get_a_processing(db, username, preprocessingid)
    if not preprocessing:
        raise NotfoundException(f"Cannot find preprocessing with id={preprocessingid}")
    # create new psetting
    # get max of existing psettings in the give preprocessing id and add 1
    # since there are not many items in a preprocessing, sorting it is acceptable
    # subquery is another way, but not needed
    # subqry = db.query(func.max(models.PSetting.order)).filter(models.PSetting.preprocessing_id == preprocessingid)
    # qry = db.query(models.PSetting).filter(models.PSetting.preprocessing_id == preprocessingid, models.PSetting.oder == subqry)
    _psettingWithHigherOrder = db.query(models.PSetting).filter(models.PSetting.preprocessing_id == preprocessingid).order_by(models.PSetting.order.desc()).first()
    if _psettingWithHigherOrder:
        order = _psettingWithHigherOrder.order + 1
    else:
        order = 1
    psetting = models.PSetting( series_id=seriesid, preprocessing_id=preprocessingid, 
                                background=serie.background, stddev=serie.stddev,
                                threshold=serie.background,
                                unit=serie.unit, pixelWidth=serie.pixelWidth,
                                pixelHeight=serie.pixelHeight, pixelDepth=serie.pixelDepth, 
                                order=order)
    db.add(psetting)
    db.flush()
    db.commit()
    db.refresh(psetting)
    psetting.series = serie
    # not sure why removing this resulting in empty series :(
    logger.debug(f"New psetting path {psetting.series.path}")
    return psetting


def get_psetting(db: Session, username: str, psetting_id: int):
    _psetting = db.query(models.PSetting).filter(models.PSetting.id == psetting_id).first()
    if _psetting:
        _series_id = _psetting.series_id
        _psetting.series = get_one_series(db, _series_id)
    return _psetting

def delete_psetting(db: Session, username: str, psetting_id: int):
    psetting = db.query(models.PSetting).filter(models.PSetting.id == psetting_id).first()
    if psetting:
        db.delete(psetting)
        db.commit()

def update_preprocessing(db: Session, username: str, preprocessingid: int, combine: bool, outputPath: str):
    preprocessing = get_a_processing(db, username, preprocessingid)
    if preprocessing == None:
        raise NotfoundException(f"Cannot find preprocessing with id={preprocessingid}")
    preprocessing.combine = combine
    preprocessing.outputPath = outputPath
    db.commit()
    return preprocessing

def update_psetting(db: Session, username: str, psetting_id: int, psetting: schemas.PSettingCreate):
    _db_psetting = db.query(models.PSetting).filter(models.PSetting.id == psetting_id).first()
    if not _db_psetting:
        raise NotfoundException(f"Cannot find psetting with id={psetting_id}")
    # update decon
    existing_psetting_dict = row2dict(_db_psetting, True)
    stored_psetting_model = schemas.PSetting(**existing_psetting_dict)
    update_psetting_data = psetting.dict(exclude_unset=True)
    updated_psetting_item = stored_psetting_model.copy(update=update_psetting_data)
    updated_psetting_item_dict = updated_psetting_item.dict()
    db.query(models.PSetting).filter(models.PSetting.id == psetting_id).update(updated_psetting_item_dict)
    db.commit()

#### macro page
def get_macro(db: Session, username: str):
    return db.query(models.Macro).\
            filter(models.Macro.username == username).\
            first()

def create_new_macro(db: Session, username: str, payload: schemas.MacroCreate):
    macro = models.Macro(**payload.dict())
    db.add(macro)
    db.commit()
    db.flush()
    #db.refresh(macro)
    return macro

def update_macro(db: Session, username: str, macro_id: int, payload: schemas.MacroCreate ):
    a_macro = get_a_macro(db, username, macro_id)
    if a_macro == None:
        raise NotfoundException(f"Cannot find preprocessing with id={macro_id}")
    a_macro.outputPath = payload.outputPath
    a_macro.inputs = payload.inputs
    a_macro.inputPaths = payload.inputPaths
    
    a_macro.instances = payload.instances
    a_macro.gpus = payload.gpus
    a_macro.mem = payload.mem

    db.commit()
    

# get a macro
def get_a_macro(db: Session, username: str, macro_id: int):
    return db.query(models.Macro).\
            filter(models.Macro.id == macro_id).\
            filter(models.Macro.username == username).\
            first()



def create_macro_and_job(db: Session, username: str, email: str, macro_id:int, sendemail: bool):
    macro = get_a_macro(db, username, macro_id)
    if not macro: 
        raise NotfoundException(f"Cannot find macro with id={macro_id}")
    #create new macro for the job first
    db_macro = models.Macro(outputPath = macro.outputPath, 
                            inputs = macro.inputs, 
                            inputPaths = macro.inputPaths, 
                            instances = macro.instances, mem = macro.mem, gpus = macro.gpus) 
    db.add(db_macro)
    db.flush()
    #now create job
    job = models.Job(id=shortuuid.uuid(), username=username, email=email, decon_id=None, convert_id=None, preprocessing_id=None, macro_id=db_macro.id, sendemail=sendemail )
    db.add(job)
    db.flush()
    db.commit()
    return job

###Update api settings

def get_config(db: Session):
    return db.query(models.ConfigSetting).\
        filter(models.ConfigSetting.apiname != None).\
        filter(models.ConfigSetting.metadatatag != None).\
        filter(models.ConfigSetting.updatedby != None).\
        filter(models.ConfigSetting.updatedon != None).\
        first()


def create_config_setting(db: Session, username: str, api:str, metadata:str):
    # check if exists
    db_config_setting =  models.ConfigSetting(apiname = api, metadatatag= metadata, updatedby = username)
    db.add(db_config_setting)
    db.flush()
    db.commit()
    


def update_config_setting(db:Session, username: str, api:str, metadata:str):
    current_config = get_config(db)
    
    if not current_config:
        create_config_setting(db,username,api,metadata)
    else:
        
        
        current_config.apiname = api
        current_config.metadatatag = metadata
        current_config.updatedby = username
       #current_config.updatedon = datetime.datetime.utcnow() 
    
    db.commit()
    return current_config



