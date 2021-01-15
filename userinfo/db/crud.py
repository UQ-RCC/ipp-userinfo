import base64
from sqlalchemy.orm import Session

from . import models, schemas

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
    return db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).one()
    
def delete_bookmark(db: Session, bookmark_id: int):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).one()
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
    series = db.query(models.Series).filter(models.Series.id == series_id).one()
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
        print ("===============")
        print (f"decoded path: {decoded_path}") 
        # a simple join
        for d, s in db.query(models.Decon, models.Series).\
                    filter(models.Decon.series_id == models.Series.id).\
                    filter(models.Decon.deconpage_id == username).\
                    filter(models.Series.path == decoded_path).all():
            decons.append(d)
        print (len(decons))
    else:
        decons = db_deconpage.decons
    return decons
    
def get_decon_from_deconpage(db: Session, usename: str, deconid: int):
    decon = db.query(models.Decon).\
                filter(models.Decon.id == deconid).\
                filter(models.Decon.deconpage_id == usename).\
                first()
    return decon

def create_decon_and_jobs(db:Session, username: str, decon_id: int, numberofjobs: int):
    """Create a new decon from the given decon_id, and create jobs with it"""
    decon = db.query(models.Decon).\
                filter(models.Decon.id == deconid).\
                filter(models.Decon.deconpage_id == usename).\
                one()
    if not decon:
        raise NotfoundException("Cannot find the given decon under this username")
    # create decon first
    db_decon = models.Decon(setting_id = decon.setting_id,
                            series_id = decon.series_id)
    db.add(db_decon)
    db.flush()
    # create jobs accordinly
    created_jobs = []
    for i in range(numberofjobs):
        db_job = models.Job(username = username, decon_id = db_decon.id)
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
    return db.query(models.Series).filter(models.Series.id == serie_id).one()

def get_one_series_by_path(db: Session, path: str):
    return db.query(models.Series).filter(models.Series.path == path).all()

def create_series(db: Session, series: schemas.SeriesCreate):
    stored_serie = get_one_series_by_path(db, series.path)
    if stored_serie:
        raise AlreadyExistException('Series with given path already exists')
    db_serie = models.Series(**series.dict())
    db.add(db_serie)
    print ("adding series")
    db.commit()
    db.refresh(db_serie)
    print (db_serie)
    return db_serie

def update_serie(db: Session, serie_id: int, series: schemas.SeriesCreate):
    db.query(models.Series).filter(models.Series.id == serie_id).update(series.dict())
    db.commit()

## settings
def get_all_settings(db: Session):
    return db.query(models.Setting).all()

def get_one_setting(db: Session, setting_id: int):
    return db.query(models.Setting).filter(models.Setting.id == setting_id).one()

def update_setting(db: Session, username: str, setting_id: int, setting: schemas.SettingCreate):
    db.query(models.Setting).filter(models.Setting.id == setting_id).update(setting.dict())
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
            one()

def delete_template(db: Session, template: models.Template):
    template = db.query(models.Template).\
                filter(models.Template.username == username).\
                filter(models.Template.id == templateid).\
                one()
    db.delete(template)
    db.commit()


############# jobs #################
def get_jobs(db:Session, username: str):
    return db.query(models.Job).\
            filter(models.Job.username == username).\
            all()

def get_job(db:Session, username: str, jobid: str):
    return db.query(models.Job).\
            filter(models.Job.username == username).\
            filter(models.Job.id == jobid).\
            one()


def update_job(db:Session, username: str, jobid: str, job: schemas.JobCreate):
    db.query(models.Job).\
        filter(models.Job.username == username).\
        filter(models.Job.id == jobid).\
        update(job.dict())
    db.commit()


