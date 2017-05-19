# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


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
    user_name = Column(String, nullable=False)
    user_password = Column(String, nullable=False)
    lnk_users_cars = relationship('Cars')
