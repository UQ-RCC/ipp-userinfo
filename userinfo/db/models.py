import enum, datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum, DateTime, Interval,func
from sqlalchemy.orm import relationship

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy_json import mutable_json_type
from sqlalchemy import PickleType
from datetime import timezone

from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy_json import NestedMutable, MutableDict

import shortuuid

from .database import Base
import pytz

class FilesExplorer(Base):
    __tablename__ = 'filesexplorers'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, index=False, nullable=False)
    component = Column(String, unique=False, index=False, nullable=False)
    currentpath = Column(String, unique=False, index=False, nullable=False)
    filters = Column(String, unique=False, index=False, nullable=True)
    bookmarks = relationship("Bookmark", back_populates="filesexplorer")
    lastpaths = Column(MutableList.as_mutable(PickleType), default=[])

class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=False, nullable=False)
    path = Column(String, unique=False, index=False, nullable=False)
    filesexplorer_id = Column(Integer, ForeignKey("filesexplorers.id"))
    filesexplorer = relationship("FilesExplorer", back_populates="bookmarks")

class Unit(enum.Enum):
    nm = 'nm'
    µm = 'µm'
    mm = 'mm'
    inch = 'inch'
    pixel = 'pixel'

###############################################################################
# Series values - raw values
class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, primary_key=False, unique=True, index=True, nullable=False)
    # metadata
    isfolder = Column(Boolean, unique=False, index=False, nullable=False, default=True)
    dr = Column(Float, primary_key=False, index=False, nullable=True)
    dz = Column(Float, primary_key=False, index=False, nullable=True)
    x = Column(Integer, primary_key=False, index=False, nullable=True)
    y = Column(Integer, primary_key=False, index=False, nullable=True)
    z = Column(Integer, primary_key=False, index=False, nullable=True)
    c = Column(Integer, primary_key=False, index=False, nullable=True)
    t = Column(Integer, primary_key=False, index=False, nullable=True)
    maxFileSizeInMb = Column(Float, primary_key=False, index=False, nullable=True)     
    total = Column(Integer, primary_key=False, index=False, nullable=True)
    outputPath = Column(String, unique=False, index=False, nullable=True)
    background = Column(Float, primary_key=False, index=False, nullable=True)    
    stddev = Column(Float, primary_key=False, index=False, nullable=True)
    unit = Column(Enum(Unit), unique=False, index=False, nullable=True)
    pixelWidth = Column(Float, primary_key=False, index=False, nullable=True) 
    pixelHeight = Column(Float, primary_key=False, index=False, nullable=True) 
    pixelDepth = Column(Float, primary_key=False, index=False, nullable=True) 
    # decon
    decons = relationship("Decon", back_populates="series")
    # decon = relationship("Decon", uselist=False, back_populates="series")
    # psettings
    psettings = relationship("PSetting", back_populates="series")
    
    


###############################################################################
# Settings
class PsfTypes(enum.Enum):
    Widefield = 0
    Confocal = 1
    TwoPhoton = 2
    LightSheet = 3
    SpinningDisk = 4
    RCM = 6
    iSIM = 7
    SoRa = 8
    NL5 = 9
    RCM2 = 10

class PsfModels(enum.Enum):
    Scalar = 0
    Vectorial = 1

class SlitDirection(enum.Enum):
    Vertical = 0
    Horizontal = 1

class TubeLens (enum.Enum):
    Leica = 0
    Nikon = 1
    Olympus = 2
    Zeiss = 3

class MediumRIOptions(enum.Enum):
    Presets = -1
    Water = 1.33
    Vectashield = 1.46
    ProlongGold = 1.44
    FluoromountG = 1.4
    MowiolLowRI = 1.41
    MowiolHighRI = 1.49
    Glycerol = 1.45

class ObjectiveRIOptions(enum.Enum):
    Presets = -1
    Air = 1
    Water = 1.33
    OilTypeA = 1.515
    OilTypeFN = 1.518
    Glycerol = 1.45
    Silicon = 1.41


class BackgroundType(enum.Enum):
    Non = -1
    OneP = 0.01
    FiveP = 0.05
    TenP = 0.1
    TwentyfiveP = 0.25
    Manual = 0

class RegularizationType(enum.Enum):
    Non = 0
    TV = 1
    Entropy = 2

class PreFilterType(enum.Enum):
    Non = 0
    GaussianImage = 1
    GaussianImageAndPSF = 2
    MedianImage = 3

class PostFilterType(enum.Enum):
    Non = 0
    Gaussian = 1
    Median = 2
    SharpenFilter = 3

class ScalingType(enum.Enum):
    Default = 0 
    SameAsInput = 1

class FileFormatType(enum.Enum):
    TIFF = 0
    OMETIFF = 1
    HDF5 = 2
    Imaris50 = 3
    Slidebook60 = 4
    ArivisSIS = 5
    IMS = 6

class SplitChannelType(enum.Enum):
    NoSplit = 0 
    SplitChannels = 1
    SplitTimepoints = 2
    SplitChannelsAndTimepoints = 3


class Setting(Base):
    '''
    This table is in fact a series values - nothing more
    '''
    __tablename__ = 'setting'
    id = Column(Integer, primary_key=True, index=True)
    outputPath = Column(String, primary_key=False, unique=False, index=False, nullable=True)
    ### illumination type
    psfType = Column(Enum(PsfTypes), primary_key=False, index=False, nullable=False, default=PsfTypes.LightSheet) 
    ### metadata fields
    dr = Column(Float, primary_key=False, index=False, nullable=True)
    dz = Column(Float, primary_key=False, index=False, nullable=True)
    readSpacing = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    x = Column(Integer, primary_key=False, index=False, nullable=True)
    y = Column(Integer, primary_key=False, index=False, nullable=True)
    z = Column(Integer, primary_key=False, index=False, nullable=True)
    swapZT = Column(Boolean, primary_key=False, index=False, nullable=False, default=False)
    c = Column(Integer, primary_key=False, index=False, nullable=True)
    t = Column(Integer, primary_key=False, index=False, nullable=True)
    ### PSF
    generatePsf = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    ############# for auto generate psf
    psfModel = Column(Enum(PsfModels), primary_key=False, index=False, nullable=True, default=PsfModels.Scalar) 
    # ns = mediumRIOption
    ns = Column(Float, primary_key=False, index=False, nullable=True, default=1.33)
    mediumRIOption = Column(Enum(MediumRIOptions), primary_key=False, index=False, nullable=True, default=MediumRIOptions.Water)
    objMagnification = Column(Float, primary_key=False, index=False, nullable=True)
    slitWidth = Column(Float, primary_key=False, index=False, nullable=True)
    slitDirection = Column(Enum(SlitDirection), primary_key=False, index=False, nullable=True)
    lensFocalLength = Column(Enum(TubeLens), primary_key=False, index=False, nullable=True)
    #
    NA = Column(Float, primary_key=False, index=False, nullable=True, default=1.4)
    lightSheetIlluminationNA = Column(Float, primary_key=False, index=False, nullable=True, default=0.5)
    # RI = objectiveRIOption
    RI = Column(Float, primary_key=False, index=False, nullable=True, default=1.33)
    objectiveRIOption = Column(Enum(ObjectiveRIOptions), primary_key=False, index=False, nullable=True, default=ObjectiveRIOptions.Water)
    ############# for using psf file
    psfFile = Column(String, primary_key=False, unique=False, index=False, nullable=True)
    psfDr = Column(Float, primary_key=False, index=False, nullable=True)
    psfDz = Column(Float, primary_key=False, index=False, nullable=True)
    psfReadSpacing = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    psfX = Column(Integer, primary_key=False, index=False, nullable=True)
    psfY = Column(Integer, primary_key=False, index=False, nullable=True)
    psfZ = Column(Integer, primary_key=False, index=False, nullable=True)
    swapPsfZT = Column(Boolean, primary_key=False, index=False, nullable=False, default=False)
    psfC = Column(Integer, primary_key=False, index=False, nullable=True)
    psfT = Column(Integer, primary_key=False, index=False, nullable=True)
    
    ### deskew
    deskew = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    keepDeskew = Column(Boolean, primary_key=False, index=False, nullable=True)
    background = Column(Float, primary_key=False, index=False, nullable=True)    
    stddev = Column(Float, primary_key=False, index=False, nullable=True)    
    unit = Column(Enum(Unit), unique=False, index=False, nullable=True)
    pixelWidth = Column(Float, primary_key=False, index=False, nullable=True) 
    pixelHeight = Column(Float, primary_key=False, index=False, nullable=True) 
    pixelDepth = Column(Float, primary_key=False, index=False, nullable=True)
    angle = Column(Float, primary_key=False, index=False, nullable=True)
    threshold = Column(Float, primary_key=False, index=False, nullable=True)    

    ### iterations
    channels = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    backgroundType = Column(Enum(BackgroundType), primary_key=False, index=False, nullable=True, default=BackgroundType.Non)
    saveEveryIterations = Column(Integer, primary_key=False, index=False, nullable=False, default=0)

    ### noise surpression
    regularizationType = Column(Enum(RegularizationType), primary_key=False, index=False, nullable=True, default=RegularizationType.Non)
    automaticRegularizationScale = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    regularization = Column(Float, primary_key=False, index=False, nullable=True)
    prefilter = Column(Enum(PreFilterType), primary_key=False, index=False, nullable=True, default=PreFilterType.Non)
    postfilter = Column(Enum(PostFilterType), primary_key=False, index=False, nullable=True, default=PostFilterType.Non)

    ### advanced
    blindDeconvolution = Column(Boolean, primary_key=False, index=False, nullable=False, default=False)
    padding = Column(mutable_json_type(dbtype=JSONB, nested=False), nullable=True)
    tiling = Column(mutable_json_type(dbtype=JSONB, nested=False), nullable=True)
    scaling = Column(Enum(ScalingType), primary_key=False, index=False, nullable=True, default=ScalingType.SameAsInput)
    fileformat = Column(Enum(FileFormatType), primary_key=False, index=False, nullable=True, default=FileFormatType.TIFF)
    split = Column(Enum(SplitChannelType), primary_key=False, index=False, nullable=True, default=SplitChannelType.NoSplit)
    splitIdx = Column(Integer, primary_key=False, index=False, nullable=True, default=0)

    ### devices
    instances = Column(Integer, primary_key=False, index=False, nullable=True)
    mem = Column(Float, primary_key=False, index=False, nullable=True)
    gpus = Column(Integer, primary_key=False, index=False, nullable=True)

    # is this setting valid
    valid = Column(Boolean, primary_key=False, index=False, default=False)
    # template ref
    template = relationship("Template", uselist=False, back_populates="setting")
    # decon
    decon = relationship("Decon", uselist=False, back_populates="setting")

    
class Template(Base):
    '''
    This table contains templates - settins with a name
    '''
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, primary_key=False, index=False, nullable=False)
    name = Column(String, primary_key=False, index=False, nullable=False)
    # one template corresponds to one setting
    # setting
    setting_id = Column(Integer, ForeignKey('setting.id'))
    setting = relationship("Setting", back_populates="template")

class PcalSetting(Base):
    '''
    This table contains pinhole calculator settings from gobal and local user
    '''
    
    __tablename__ = 'pcalsetting'
    id = Column(Integer, primary_key=True, index=True)
    username =  Column(String, primary_key=False, index=False, nullable=False)
    name = Column(String, primary_key=False, index=False, nullable=False)
    illuminationtype = Column(String, primary_key=False, index=False, nullable=True)
    objmagnification = Column(Float, primary_key=False, index=False, nullable=True)  
    auxmagnification = Column(Float, primary_key=False, index=False, nullable=True)  
    pinholesize = Column(Float, primary_key=False, index=False, nullable=True) 
    model = Column(String, primary_key=False, index=False, nullable=True)
    pinholeshape = Column(String, primary_key=False, index=False, nullable=True)
    pinholeside = Column(String, primary_key=False, index=False, nullable=True)
    shapefactor = Column(Float, primary_key=False, index=False, nullable=True) 
    sysmagnification = Column(Float, primary_key=False, index=False, nullable=True) 
    pinholespacing = Column(Float, primary_key=False, index=False, nullable=True) 
    pinholeradius = Column(Float, primary_key=False, index=False, nullable=True) 

class Decon(Base):
    __tablename__ = 'decon'
    id = Column(Integer, primary_key=True, index=True)
    # setting
    setting_id = Column(Integer, ForeignKey('setting.id'))
    setting = relationship("Setting", back_populates="decon")
    # series
    series_id = Column(Integer, ForeignKey('series.id'))
    series = relationship("Series", back_populates="decons")
    ## decon page
    deconpage_id = Column(String, ForeignKey("deconpage.username"), nullable=True)
    deconpage = relationship("DeconPage", back_populates="decons")
    ## job
    jobs = relationship("Job", back_populates="decon")
    # steps
    step = Column(Integer, primary_key=False, index=False, default=1)
    visitedSteps = Column(MutableList.as_mutable(PickleType), default=[])
    selected = Column(Boolean, primary_key=False, index=False, default=False)
    api = Column(String,primary_key=False, index=False)
    
class DeconPage(Base):
    __tablename__ = 'deconpage'
    username = Column(String, primary_key=True, index=True)
    decons = relationship("Decon", back_populates="deconpage")
    
class ConfigSetting(Base):
    __tablename__ = 'configsetting'
    apiname = Column(String, primary_key=False, index=False, nullable=True)
    metadatatag = Column(String, primary_key=False, index=False, nullable=True)
    updatedby = Column(String, primary_key=True, index=True, nullable=False)
    updatedon = Column(DateTime(timezone=True), primary_key=False, index=False, nullable=True, default=func.timezone('UTC', func.now()), onupdate=func.timezone('UTC', func.now()))
   


def generate_uuid():
    return shortuuid.uuid()

    
##### preprocessing ###############################
class PSetting(Base):
    __tablename__ = 'psetting'
    id = Column(Integer, primary_key=True, index=True)
    ### deskew
    deskew = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    keepDeskew = Column(Boolean, primary_key=False, index=False, nullable=True, default=True)
    background = Column(Float, primary_key=False, index=False, nullable=True)    
    stddev = Column(Float, primary_key=False, index=False, nullable=True)    
    unit = Column(Enum(Unit), unique=False, index=False, nullable=True)
    pixelWidth = Column(Float, primary_key=False, index=False, nullable=True) 
    pixelHeight = Column(Float, primary_key=False, index=False, nullable=True) 
    pixelDepth = Column(Float, primary_key=False, index=False, nullable=True)
    angle = Column(Float, primary_key=False, index=False, nullable=False, default=32.8)
    threshold = Column(Float, primary_key=False, index=False, nullable=False, default=0)    
    ### 
    centerAndAverage = Column(Boolean, primary_key=False, index=False, nullable=False, default=False)
    order = Column(Integer, primary_key=False, index=False, default=1)


    # series
    series_id = Column(Integer, ForeignKey('series.id'))
    series = relationship("Series", back_populates="psettings")
    
    # preprocessing
    preprocessing_id = Column(Integer, ForeignKey('preprocessing.id'), nullable=True)
    preprocessing = relationship("Preprocessing", uselist=False, back_populates="psettings")

# make sure to create a new Preprocessing whenever a submission is done
class Preprocessing(Base):
    __tablename__ = 'preprocessing'
    id = Column(Integer, primary_key=True, index=True)
    # setting
    psettings = relationship("PSetting", back_populates="preprocessing")
    
    combine = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    
    outputPath = Column(String, primary_key=False, unique=False, index=False, nullable=True)
    ## job
    job = relationship("Job", uselist=False, back_populates="preprocessing")
    ## preprocessingpage
    preprocessingpage_id = Column(String, ForeignKey("preprocessingpage.username"), nullable=True)
    preprocessingpage = relationship("PreprocessingPage", back_populates="preprocessing")


class PreprocessingPage(Base):
    __tablename__ = 'preprocessingpage'
    username = Column(String, primary_key=True, index=True)
    preprocessing = relationship("Preprocessing", uselist=False, back_populates="preprocessingpage")

##### macro ##################################

class Macro(Base):
    __tablename__ = 'macro'
    id = Column(Integer, primary_key=True, index=True)
    outputPath = Column(String, primary_key=False, unique=False, index=False, nullable=True)
    username = Column(String, primary_key=False, unique=False, index=False, nullable=True)
    inputs = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    inputPaths = Column(MutableList.as_mutable(PickleType), default=[])
    ### devices
    instances = Column(Integer, primary_key=False, index=False, nullable=True)
    mem = Column(Float, primary_key=False, index=False, nullable=True)
    gpus = Column(Integer, primary_key=False, index=False, nullable=True)
    ## job
    job = relationship("Job", uselist=False, back_populates="macro")

##### converter ###############################
class Convert(Base):
    __tablename__ = 'convert'
    id = Column(Integer, primary_key=True, index=True)
    ## setting
    outputPath = Column(String, primary_key=False, unique=False, index=False, nullable=True, default='')
    prefix = Column(String, primary_key=False, unique=False, index=False, nullable=True, default='')
    # [{'label': 'Bigload', 'value': 'bigload'},
    #            {'label': 'Chunked', 'value': 'chunked'},
    #            {'label': 'Hyperslab', 'value': 'hyperslab'}]
    method = Column(String, primary_key=False, unique=False, index=False, nullable=True, default='bigload')
    # input
    inputPaths = Column(MutableList.as_mutable(PickleType), default=[])
    ## job
    job = relationship("Job", uselist=False, back_populates="convert")
    # max size of all the items selected
    maxsize = Column(String, primary_key=False, unique=False, index=False, nullable=False, default=0)
    ## preprocessingpage
    convertpage_id = Column(String, ForeignKey("convertpage.username"), nullable=True)
    convertpage = relationship("ConvertPage", back_populates="convert")

class ConvertPage(Base):
    __tablename__ = 'convertpage'
    username = Column(String, primary_key=True, index=True)
    convert = relationship("Convert", uselist=False, back_populates="convertpage")
    


# job - decon job
class Job(Base):
    __tablename__ = 'job'
    # same as job id in slurm
    id = Column(String(50), primary_key=True, default=generate_uuid())
    username = Column(String, primary_key=False, index=False, nullable=True)
    email = Column(String, primary_key=False, index=False, nullable=True)
    # job data
    jobid = Column(Integer, primary_key=False, index=False, nullable=True)
    jobname = Column(String, primary_key=False, index=False, nullable=True)
    submitted =  Column(DateTime(timezone=True), primary_key=False, index=False, nullable=False, server_default=func.timezone('UTC', func.now()))
    start =  Column(DateTime, primary_key=False, index=False, nullable=True )
    end =  Column(DateTime, primary_key=False, index=False, nullable=True)
    status = Column(String, primary_key=False, index=False, nullable=False, default='SUBMITTED')
    ## total number of files to cruch
    total = Column(Integer, primary_key=False, index=False, nullable=True, default=0)
    ## processed files so far
    success = Column(Integer, primary_key=False, index=False, nullable=True, default=0)
    fail = Column(Integer, primary_key=False, index=False, nullable=True, default=0)
    ncpus = Column(Integer, primary_key=False, index=False, nullable=True)
    nnodes = Column(Integer, primary_key=False, index=False, nullable=True)
    reqgres = Column(Integer, primary_key=False, index=False, nullable=True)
    reqmem = Column(Float, primary_key=False, index=False, nullable=True)
    # many job corresponds to one decon
    decon_id = Column(Integer, ForeignKey("decon.id"), nullable=True)
    decon =  relationship("Decon", back_populates="jobs")
    # convert
    convert_id = Column(Integer, ForeignKey("convert.id"), nullable=True)
    convert =  relationship("Convert", back_populates="job")
    # preprocessing
    preprocessing_id = Column(Integer, ForeignKey("preprocessing.id"), nullable=True)
    preprocessing =  relationship("Preprocessing", back_populates="job")
    # preprocessing
    macro_id = Column(Integer, ForeignKey("macro.id"), nullable=True)
    macro =  relationship("Macro", back_populates="job")

    # send email not or
    sendemail = Column(Boolean, primary_key=False, index=False, nullable=False, default=True)
    
