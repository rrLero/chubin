# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from my_models import Base, Notes, Cars, Users
import os
from sqlalchemy.orm import class_mapper

if os.environ.get('DATABASE_URL') is None:
    url = "postgresql:///chubin"
else:
    url = os.environ['DATABASE_URL']


engine = create_engine(url)

Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session_git = DBSession()


# parser = reqparse.RequestParser()
# parser2 = reqparse.RequestParser()


# def get_arguments_post():
#     parser.add_argument('car', type=int, location='json', required=True, help="Что то не так заполнено в car")
#     parser.add_argument('date', type=str, location='json', required=True, help="Что то не так заполнено в date")
#     parser.add_argument('km', type=int, location='json', required=True, help="Что то не так заполнено в km")
#     parser.add_argument('works', type=str, location='json', required=True, help="Что то не так заполнено в works")
#     parser.add_argument('pays', type=int, location='json', required=True, help="Что то не так заполнено в pays")
#     return parser.parse_args()
#
#
# def get_arguments_del():
#     parser2.add_argument('id_note', type=int, required=True, location='json', help="id_note - не пришел")
#     return parser2.parse_args()


# запрос для Python консоли - просто скопировать в консоль
# import requests
# x = requests.post('http://0.0.0.0:5000/', json = {'test': '1', 'test2': 2, 'test3': 3, 'test4': 4, 'test5': [1,2,3]})


def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)

# we can then use this for your particular example


class ShowCars(Resource):
    def get(self, id_car):
        query_cars = session_git.query(Cars).get(id_car)
        query_notes = session_git.query(Notes).filter(Notes.car == id_car)
        serialized_labels = [serialize(label) for label in
                             query_notes]
        session_git.close()
        return jsonify(serialized_labels)
