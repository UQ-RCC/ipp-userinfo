from typing import List

from fastapi import APIRouter, Response, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.orm import Session

import userinfo.db as udb 
import userinfo.keycloak as keycloak

router = APIRouter()

@router.get("/fileexplorer/components", response_model=List[str])
def get_filexplorer_pref(user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    db_components = udb.crud.get_filesexplorer_components(db, username)
    result = [r for r, in db_components]
    return result


@router.get("/fileexplorer/components/{component}", response_model=udb.schemas.FilesExplorer)
def get_filexplorer_pref(component: str, 
                         user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    """
    Get pref for fileexplorer from given component
    Always returns smth
    """
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    pref = udb.crud.get_filesexplorer_by_username_component(db, username, component)
    # create if not exist
    if not pref:
        default_pref_value = udb.schemas.FilesExplorerBase(
                                                            username=username, 
                                                            component=component, 
                                                            currentpath='/',
                                                            filters = ''
                                                            )
        pref = udb.crud.create_filesexplorer(db, default_pref_value)
    return pref

    

@router.put("/fileexplorer/components/{component}/{prefid}", response_model=udb.schemas.FilesExplorer)
def update_filexplorer_pref(component: str, prefid: int, pref: udb.schemas.FilesExplorerUpdate,
                        user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    """
    Update pref
    """
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    fileexplorer_pref = udb.crud.get_filesexplorer(db, prefid)
    if not fileexplorer_pref:
        return HTTPException(status_code=400, detail="Invalid prefid")
    if fileexplorer_pref.username != username:
        return HTTPException(status_code=401, detail="Cannot edit others pref")
    return udb.crud.update_filesexplorer(db, prefid, pref)


@router.post("/fileexplorer/components/{component}/{prefid}/bookmarks", response_model=udb.schemas.Bookmark)
def add_bookmark(component: str, prefid: int, bookmark: udb.schemas.BookmarkCreate,
                user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    """
    Add bookmark
    """
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    return udb.crud.create_bookmark(db, prefid, bookmark)
    

@router.delete("/fileexplorer/components/{component}/{prefid}/bookmarks/{bookmarkid}", response_model=List[udb.schemas.Bookmark])
def delete_bookmark(component: str, prefid: int, bookmarkid: int,
                    user: dict = Depends(keycloak.decode), db: Session = Depends(udb.get_db)):
    """
    Delete a bookmark
    """
    username = user.get('preferred_username')
    if not username:
        return HTTPException(status_code=400, detail="Username cannot be empty")
    db_bookmark = udb.crud.get_bookmark(db, bookmarkid)
    if db_bookmark.filesexplorer_id != prefid:
        return HTTPException(status_code=400, detail="Bookmark not belong to pref")
    udb.crud.delete_bookmark(db, bookmarkid)
    return udb.crud.get_bookmarks(db, username, component)
