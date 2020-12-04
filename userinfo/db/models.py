from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Interval
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
    filters = Column(String, unique=False, index=False)
    bookmarks = relationship("Bookmark", back_populates="filesexplorer")
    lastpaths = Column(MutableList.as_mutable(PickleType), default=[])

class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=False)
    path = Column(String, unique=False, index=False)
    filesexplorer_id = Column(Integer, ForeignKey("filesexplorers.id"))
    filesexplorer = relationship("FilesExplorer", back_populates="bookmarks")


class Job(Base):
    __tablename__ = 'jobs'
    jobid = Column(String, primary_key=True, index=True)
    username = Column(String, primary_key=False, index=False)
    jobname = Column(String, primary_key=False, index=False)
    partition = Column(String, primary_key=False, index=False)
    state = Column(String, primary_key=False, index=False)
    start = Column(DateTime, primary_key=False, index=False)
    end = Column(DateTime, primary_key=False, index=False)
    elapsed = Column(Interval, primary_key=False, index=False)
    ncpus = Column(Integer, primary_key=False, index=False)
    nnodes = Column(Integer, primary_key=False, index=False)
    nodelist = Column(String, primary_key=False, index=False)
    reqgres = Column(Integer, primary_key=False, index=False)
    # pernode
    reqmem = Column(Float, primary_key=False, index=False)
    

class Deconvolution(Base):
    """
    """
    __tablename__ = 'deconvolution'
    username = Column(String, primary_key=True, index=True)

    series = relationship("Series", back_populates="deconvolution")



class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=False, index=False)
    ### metadata here

    #####
    deconvolution_id = Column(String, ForeignKey("deconvolution.username"))
    deconvolution = relationship("Deconvolution", back_populates="series")

