# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from my_models import Notes, Cars, Users, session_git
from datetime import datetime
import time
import datetime
from flask import request, abort
from functools import wraps
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


def get_stats(users_list):
    if not users_list:
        return None, None
    else:
        km_list = []
        pay_list = []
        for user in users_list:
            km_list.append(user['km'])
            pay_list.append(user['pays'])
        payments = 0
        for pays in pay_list:
            if pays:
                payments += pays
        km_result = max(km_list) - min(km_list)
        return payments, km_result


def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)


class CreateEditDeleteNotes(Resource):
    @requires_auth
    def get(self):
        user_id = get_user_id()
        args = get_arguments_get()
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        if not date_to:
            date_to = int(time.time())+86400
        if not date_from:
            date_from = int(time.time()) - 26086400
        date_from = datetime.datetime.utcfromtimestamp(date_from)
        date_to = datetime.datetime.utcfromtimestamp(date_to)
        cars_query = session_git.query(Cars).filter(Cars.user == user_id)
        query = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id, Notes.date > date_from, Notes.date < date_to).order_by(Notes.date.desc())
        users_list = [{'date': notes.date, 'km': notes.km, 'works': notes.works,
                       'pays': notes.pays, 'id': notes.id, 'car': [serialize(car) for car in cars_query if car.id == notes.car][0]} for notes in query]
        payments, km_result = get_stats(users_list)
        session_git.close()
        return jsonify({'notes': users_list, 'payments': payments, 'run': None})
