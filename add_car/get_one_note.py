# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from my_models import Notes, Cars, Users, session_git
from datetime import datetime
import time
from flask import request, abort, jsonify
from functools import wraps
import datetime
from sqlalchemy.orm import class_mapper


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
    parser_2.add_argument('date_from', type=float, help='Timestamp')
    parser_2.add_argument('date_to', type=float, help='Timestamp')
    return parser_2.parse_args()


def get_arguments_post():
    parser.add_argument('date', type=float, location='json', required=True, help="Что то не так заполнено в date")
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


def get_stats(users_list):
    if not users_list:
        return None, None
    else:
        km_list = []
        pay_list = []
        for user in users_list:
            km_list.append(user['km'])
            pay_list.append(user['pays'])
        payments = sum(pay_list)
        km_result = max(km_list) - min(km_list)
        return payments, km_result


def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)


class GetOneNote(Resource):
    @requires_auth
    def get(self, note_id):
        user_id = get_user_id()
        notes = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id, Notes.id == note_id).first()
        if not notes:
            return {'message': 'no note with such id'}, 403
        cars_query = session_git.query(Cars).filter(Cars.user == user_id)
        users_list = {'date': notes.date, 'km': notes.km, 'works': notes.works, 'pays': notes.pays, 'id': notes.id,
                      'car': [serialize(car) for car in cars_query if car.id == notes.car][0]}
        session_git.close()
        return jsonify(users_list)