# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker


if os.environ.get('DATABASE_URL') is None:
    url = "postgresql:///chubin"
else:
    url = os.environ['DATABASE_URL']

Base = declarative_base()
engine = create_engine(url)
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session_git = DBSession()


class Cars(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    gov_number = Column(String, nullable=False)
    car_type = Column(String, nullable=False)
    gov_number_trailer = Column(String)
    user = Column(Integer, ForeignKey('users.id'), nullable=False)
    # relationships
    lnk_cars_notes = relationship('Notes')


class Notes(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    car = Column(Integer, ForeignKey('cars.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    km = Column(Integer, nullable=False)
    works = Column(String, nullable=False)
    pays = Column(Integer)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False)
    user_token = Column(String)
    lnk_users_cars = relationship('Cars')
