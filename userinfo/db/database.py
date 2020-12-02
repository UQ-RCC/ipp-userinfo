from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import userinfo.config as config

SQLALCHEMY_DATABASE_URL = (f"{config.get('database', 'type')}://"
                           f"{config.get('database', 'username')}:"
                           f"{config.get('database', 'password')}@"
                           f"{config.get('database', 'host')}/"
                           f"{config.get('database', 'name')}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
