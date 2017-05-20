# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from my_models import Base, Notes, Cars, Users
import os
from datetime import datetime


if os.environ.get('DATABASE_URL') is None:
    url = "postgresql:///chubin"
else:
    url = os.environ['DATABASE_URL']


engine = create_engine(url)

Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session_git = DBSession()


parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()


def get_arguments_post():
    parser.add_argument('date', type=str, location='json', required=True, help="Что то не так заполнено в date")
    parser.add_argument('km', type=int, location='json', required=True, help="Что то не так заполнено в km")
    parser.add_argument('works', type=str, location='json', required=True, help="Что то не так заполнено в works")
    parser.add_argument('pays', type=int, location='json', required=True, help="Что то не так заполнено в pays")
    return parser.parse_args()


# запрос для Python консоли - просто скопировать в консоль
# import requests
# x = requests.post('http://0.0.0.0:5000/', json = {'test': '1', 'test2': 2, 'test3': 3, 'test4': 4, 'test5': [1,2,3]})


class CreateEditDeleteNotes(Resource):
    def get(self, user_id):
        query = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id)
        users_list = [{'car': notes.car, 'date': notes.date, 'km': notes.km, 'works': notes.works,
                       'pays': notes.pays, 'id': notes.id} for notes in query]
        session_git.close()
        return jsonify(users_list)

    def post(self, user_id, car_id):
        args = get_arguments_post()
        cars = session_git.query(Cars).get(car_id)
        if not cars:
            return {'message': 'no car with such id'}, 401
        if cars.user != user_id:
            return {'message': 'user with such has no rights to delete this post'}, 401
        date = args.get('date')
        dt = datetime.strptime(date, "%d/%m/%Y")
        date = dt
        km = args.get('km')
        works = args.get('works')
        pays = args.get('pays')
        new_note = Notes(car=car_id, date=date, km=km, works=works, pays=pays)
        session_git.add(new_note)
        session_git.commit()
        session_git.close()
        return {'message': 'new note created'}, 201

    def delete(self, user_id, car_id):
        id_note = car_id
        query = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id)
        for note in query:
            if note.id == id_note:
                session_git.delete(note)
                session_git.commit()
                session_git.close()
                return {'message': 'note deleted'}, 202
        session_git.close()
        return {'message': 'user with such has no rights to delete this post'}, 401
