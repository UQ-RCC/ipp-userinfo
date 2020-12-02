from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_json import mutable_json_type

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

from .database import Base

class FilesExplorer(Base):
    __tablename__ = 'filesexplorers'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, index=False)
    component = Column(String, unique=False, index=False)
    currentpath = Column(String, unique=False, index=False)
    bookmarks = relationship("Bookmark", back_populates="filesexplorer")
    # lastpaths = relationship("LastPath", back_populates="filesexplorer")
    lastpaths = Column(MutableList.as_mutable(PickleType), default=[])

class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=False)
    path = Column(String, unique=False, index=False)
    
    filesexplorer_id = Column(Integer, ForeignKey("filesexplorers.id"))
    filesexplorer = relationship("FilesExplorer", back_populates="bookmarks")

    