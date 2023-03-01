from typing import List, Optional

from pydantic import BaseModel, Json
from datetime import datetime
from . import models

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
    filters: str

class FilesExplorerUpdate(BaseModel):
    currentpath: str
    filters: str

class FilesExplorer(FilesExplorerBase):
    id: int
    bookmarks: List[Bookmark] = []
    lastpaths: List[str] = []
    
    class Config:
        orm_mode = True

#################################
### Templates
#################################
class TemplateBase(BaseModel):
    username: str
    name: str 
    setting_id: int

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int

    class Config:
        orm_mode = True

#################################
#### Pinhole calculator settings
#################################
class PcalSettingBase(BaseModel):
    username: str
    name: str
    illuminationtype: Optional[str] = None
    objmagnification: Optional[float] = None
    auxmagnification: Optional[float] = None
    pinholesize: Optional[float] = None
    model: Optional[str] = None
    pinholeshape: Optional[str] = None
    pinholeside: Optional[str] = None
    shapefactor: Optional[float] = None
    sysmagnification: Optional[float] = None
    pinholespacing: Optional[float] = None
    pinholeradius: Optional[float] = None

class PcalSettingCreate(PcalSettingBase):
    pass

class PcalSetting(PcalSettingBase):
    id: int

    class Config:
        orm_mode = True

#################################
### Job
#################################
class JobBase(BaseModel):
    username: str = None
    email: str = None
    jobid: Optional[int] = None
    jobname: Optional[str] = None
    start: Optional[datetime] = None 
    end: Optional[datetime] = None 
    status: str = 'SUBMITTED'
    total: Optional[int] = None
    success: Optional[int] = None
    fail: Optional[int] = None
    ncpus: Optional[int] = None
    nnodes: Optional[int] = None
    reqgres: Optional[int] = None
    reqmem: Optional[float] = None
    decon_id: Optional[int] = None
    convert_id: Optional[int] = None
    preprocessing_id: Optional[int] = None
    sendemail: bool = True

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: str
    
    class Config:
        orm_mode = True



#################################
### decons
#################################
class DeconBase(BaseModel):
    setting_id: int
    series_id: int
    step: int = 1
    selected: bool = False
    visitedSteps: List[int] = []
    
class DeconCreate(DeconBase):
    pass

class Decon(DeconBase):
    id: int
    deconpage_id: str
    jobs: List[Job] = []
    class Config:
        orm_mode = True




##################################
### decon page
##################################
class DeconPage(BaseModel):
    username: str
    decons: List[Decon] = []

    class Config:
        orm_mode = True


#################################
### Setting
#################################
class SettingBase(BaseModel):
    outputPath: Optional[str] = None
    psfType : models.PsfTypes = models.PsfTypes.LightSheet
    ### metadata fields
    dr : Optional[float] = None 
    dz : Optional[float] = None
    readSpacing : Optional[bool] = None
    x : Optional[int] = None
    y : Optional[int] = None
    z : Optional[int] = None
    c : Optional[int] = None
    t : Optional[int] = None
    swapZT : Optional[bool] = None
    ### PSF
    generatePsf : Optional[bool] = None
    psfModel : models.PsfModels = models.PsfModels.Scalar
    ns : Optional[float] = None
    mediumRIOption : models.MediumRIOptions = models.MediumRIOptions.Water
    NA : Optional[float] = None
    lightSheetIlluminationNA : Optional[float] = None
    RI : Optional[float] = None
    objectiveRIOption : models.ObjectiveRIOptions = models.ObjectiveRIOptions.Water
    psfFile : Optional[str] = None
    psfDr : Optional[float] = None
    psfDz : Optional[float] = None
    psfReadSpacing : Optional[bool] = None
    psfX : Optional[int] = None
    psfY : Optional[int] = None
    psfZ : Optional[int] = None
    swapPsfZT : Optional[bool] = None
    psfC : Optional[int] = None
    psfT : Optional[int] = None
    ### deskew
    deskew : Optional[bool] = None
    keepDeskew : Optional[bool] = None
    background : Optional[float] = None
    stddev : Optional[float] = None
    unit : Optional[models.Unit] = None
    pixelWidth : Optional[float] = None
    pixelHeight : Optional[float] = None
    pixelDepth : Optional[float] = None
    angle: Optional[float] = None
    threshold: Optional[float] = None
    ### iterations
    channels : list = []
    backgroundType : models.BackgroundType = models.BackgroundType.Non
    saveEveryIterations : Optional[int] = None
    ### noise surpression
    regularizationType : models.RegularizationType = models.RegularizationType.Non
    automaticRegularizationScale : Optional[bool] = None
    regularization : Optional[float] = None
    prefilter : models.PreFilterType = models.PreFilterType.Non
    postfilter : models.PostFilterType = models.PostFilterType.Non
    ### advanced
    blindDeconvolution : Optional[bool] = None
    padding : dict = {}
    tiling : dict = {}
    scaling : models.ScalingType = models.ScalingType.SameAsInput
    fileformat : models.FileFormatType = models.FileFormatType.TIFF
    split : models.SplitChannelType = models.SplitChannelType.NoSplit
    splitIdx : Optional[int] = None
    ### devices
    instances : Optional[int] = None
    mem : Optional[float] = None
    gpus : Optional[int] = None
    valid: bool = False

class SettingCreate(SettingBase):
    pass

class Setting(SettingBase):
    id: int
    template: Template = None
    decon: Decon = None
    class Config:
        orm_mode = True



#################################
### Series
#################################
class SeriesBase(BaseModel):
    path: str
    isfolder: Optional[bool] = None
    dr: Optional[float] = None
    dz: Optional[float] = None
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None
    c: Optional[int] = None
    t: Optional[int] = None
    maxFileSizeInMb: Optional[float] = None
    total: Optional[int] = None
    outputPath: Optional[str] = None
    background: Optional[float] = None
    stddev: Optional[float] = None
    unit: Optional[models.Unit] = None
    pixelWidth: Optional[float] = None
    pixelHeight: Optional[float] = None
    pixelDepth: Optional[float] = None
    
class SeriesCreate(SeriesBase):
    pass

class Series(SeriesBase):
    id: int
    # decons: List[Decon] = [] --> uncomment htis will fali at get series
    
    class Config:
        orm_mode = True


#################################
### Converting
#################################
class ConvertBase(BaseModel):
    outputPath: Optional[str] = ''
    prefix: Optional[str] = ''
    method: Optional[str] = 'bigload'
    # input
    inputPaths: List[str] = []
    maxsize: int = 0
    

class ConvertCreate(ConvertBase):
    pass

class Convert(ConvertBase):
    id: int
    ## job
    job: Job = None

    class Config:
        orm_mode = True

class ConvertPage(BaseModel):
    username: str
    convert: Convert = None
    class Config:
        orm_mode = True

#################################
### Preprocessing
#################################

class PreprocessingBase(BaseModel):
    preprocessingpage_id: str
    combine: bool = True
    outputPath: Optional[str] = None

class PreprocessingCreate(PreprocessingBase):
    pass



#################################
### Preprocessingsetting
#################################
class PSettingBase(BaseModel):
    preprocessing_id: Optional[int] = None
    ### deskew
    deskew: bool = True
    keepDeskew: bool = True
    background: Optional[float] = None   
    stddev: Optional[float] = None
    unit: Optional[models.Unit] = None
    pixelWidth: Optional[float] = None
    pixelHeight: Optional[float] = None
    pixelDepth: Optional[float] = None
    angle: Optional[float] = None
    threshold: Optional[float] = None 
    ### 
    centerAndAverage: bool = False
    order: int
    
    
class PSettingCreate(PSettingBase):
    pass

class PSetting(PSettingBase):
    id: int
    class Config:
        orm_mode = True

class Preprocessing(PreprocessingBase):
    id: int
    job: Job = None
    psettings: List[PSetting] = []
    class Config:
        orm_mode = True

#################################
### Preprocessing page
#################################
class PreprocessingPageBase(BaseModel):
    username: str

class PreprocessingPage(PreprocessingPageBase):
    preprocessing: Preprocessing = None
    class Config:
        orm_mode = True