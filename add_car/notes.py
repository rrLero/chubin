# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from my_models import Notes, Cars, Users, session_git
from datetime import datetime
from flask import request, abort
from functools import wraps


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        parser_auth = reqparse.RequestParser()
        parser_auth.add_argument('token', type=str)
        args = parser_auth.parse_args()
        auth = args.get('token')
        user_id = kwargs['user_id']
        if not auth:  # no header set
            abort(401)
        user = session_git.query(Users).filter(Users.id == user_id, Users.user_token == auth).first()
        if user is None:
            abort(401)
        return f(*args, **kwargs)
    return decorated

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
    @requires_auth
    def get(self, user_id):
        user_query = session_git.query(Users).get(user_id)
        if not user_query:
            return 'Page no found', 404
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
