from sqlalchemy import Table, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime
Base = declarative_base()
import config

class DataPath(Base):
    __tablename__ = 'datapath'
    path = Column(String(255), primary_key=True)
    units = Column(String(50))
    points = relationship("DataPoint")
    created = Column(DateTime, default=datetime.datetime.utcnow())
    updated = Column(DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

class DataPoint(Base):
    __tablename__ = 'datapoint'
    id = Column(Integer, primary_key=True)
    value = Column(String(50))
    when = Column(DateTime, default=datetime.datetime.utcnow())
    path = Column(String(255), ForeignKey('datapath.path'))

class RejectedSubmission(Base):
    __tablename__ = 'rejectedsubmission'
    id = Column(Integer, primary_key=True)
    data = Column(Text)
    when = Column(DateTime, default=datetime.datetime.utcnow())
    offset = Column(Integer)

from sqlalchemy import create_engine
engine = create_engine(config.settings['database_connection'])

engine.echo = False

from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)