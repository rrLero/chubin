# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from my_models import Notes, Cars, Users, session_git
from datetime import datetime
import time
import datetime
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

parser_2 = reqparse.RequestParser()


def get_arguments_get():
    parser_2.add_argument('token', help="token")
    parser_2.add_argument('date_from', type=float, help='Timestamp')
    parser_2.add_argument('date_to', type=float, help='Timestamp')
    return parser_2.parse_args()


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
        args = get_arguments_get()
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        if not date_to:
            date_to = int(time.time())
        if not date_from:
            date_from = int(time.time()) - 2600000
        date_from = datetime.datetime.utcfromtimestamp(date_from)
        date_to = datetime.datetime.utcfromtimestamp(date_to)
        cars_query = session_git.query(Cars).filter(Cars.user == user_id)
        query = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id, Notes.date > date_from, Notes.date < date_to).order_by(Notes.date)
        users_list = [{'car': notes.car, 'date': notes.date, 'km': notes.km, 'works': notes.works,
                       'pays': notes.pays, 'id': notes.id, 'car_name': [car.car_type for car in cars_query if car.id == notes.car]} for notes in query]
        session_git.close()
        return jsonify(users_list)
