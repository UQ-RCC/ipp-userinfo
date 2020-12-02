from typing import List, Optional

from pydantic import BaseModel

#################################
### bookmark
#################################
class BookmarkBase(BaseModel):
    name: str
    path: str

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id: int
    filesexplorer_id: int

    class Config:
        orm_mode = True

#################################
### filesexplorer
#################################
class FilesExplorerBase(BaseModel):
    username: str
    component: str
    currentpath: str

class FilesExplorerUpdate(BaseModel):
    currentpath: str

class FilesExplorer(FilesExplorerBase):
    id: int
    bookmarks: List[Bookmark] = []
    lastpaths: List[str] = []
    
    class Config:
        orm_mode = True
