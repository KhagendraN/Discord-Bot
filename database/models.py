from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(String)
    time = Column(String)
    subject = Column(String)
    group_name = Column(String)
    room = Column(String)
    instructor = Column(String)
    note = Column(String)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String)
    topic = Column(String)
    due_date = Column(String)

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String)
    link = Column(String)

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String)
    drive_link = Column(String)

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String)
    date = Column(String)
    time = Column(String)
    description = Column(String)
