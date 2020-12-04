from sqlalchemy.orm import Session

from . import models, schemas



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
