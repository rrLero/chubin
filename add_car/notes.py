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
        if not auth:  # no header set
            abort(401)
        user = session_git.query(Users).filter(Users.user_token == auth).first()
        if user is None:
            abort(401)
        return f(*args, **kwargs)
    return decorated

parser = reqparse.RequestParser()
parser_2 = reqparse.RequestParser()


def get_arguments_get():
    parser_2.add_argument('token', help="token")
    return parser_2.parse_args()


def get_arguments_post():
    parser.add_argument('date', type=str, location='json', required=True, help="Что то не так заполнено в date")
    parser.add_argument('km', type=int, location='json', required=True, help="Что то не так заполнено в km")
    parser.add_argument('works', type=str, location='json', required=True, help="Что то не так заполнено в works")
    parser.add_argument('pays', type=int, location='json', required=True, help="Что то не так заполнено в pays")
    parser.add_argument('token', help="token")
    return parser.parse_args()


def get_user_id():
    args = get_arguments_get()
    token = args.get('token')
    user_query = session_git.query(Users).filter(Users.user_token == token).first()
    session_git.close()
    return user_query.id


class CreateEditDeleteNotes(Resource):
    @requires_auth
    def get(self):
        user_id = get_user_id()
        query = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id)
        users_list = [{'car': notes.car, 'date': notes.date, 'km': notes.km, 'works': notes.works,
                       'pays': notes.pays, 'id': notes.id} for notes in query]
        session_git.close()
        return jsonify(users_list)

    def post(self, car_id):
        args = get_arguments_post()
        cars = session_git.query(Cars).get(car_id)
        if not cars:
            return {'message': 'no car with such id'}, 403
        token = args.get('token')
        users = session_git.query(Users).filter(Users.user_token == token).first()
        if cars.user != users.id:
            return {'message': 'you have no rights to make post'}, 401
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

    def delete(self, car_id):
        user_id = get_user_id()
        id_note = car_id
        note = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id, Notes.id == id_note).first()
        if note:
            session_git.delete(note)
            session_git.commit()
            session_git.close()
            return {'message': 'note deleted'}, 202
        session_git.close()
        return {'message': 'this user has no rights to delete this post'}, 401
