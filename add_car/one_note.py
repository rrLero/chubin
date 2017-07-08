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


class EditDeleteOneNote(Resource):
    @requires_auth
    def get(self, car_id):
        user_id = get_user_id()
        args = get_arguments_get()
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        if not date_to:
            date_to = int(time.time())+86400
        if not date_from:
            date_from = int(time.time()) - 2600000
        date_from = datetime.datetime.utcfromtimestamp(date_from)
        date_to = datetime.datetime.utcfromtimestamp(date_to)
        query = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == user_id,
                                                                                 Notes.date >= date_from,
                                                                                 Notes.date <= date_to,
                                                                                 Cars.id == car_id).order_by(Notes.date.desc())
        cars_query = session_git.query(Cars).filter(Cars.user == user_id)
        users_list = [{'date': notes.date, 'km': notes.km, 'works': notes.works,
                       'pays': notes.pays, 'id': notes.id, 'car': [serialize(car) for car in cars_query if car.id == notes.car][0]} for notes in query]
        payments, km_result = get_stats(users_list)
        session_git.close()
        return jsonify({'notes': users_list, 'payments': payments, 'run': km_result})

    @requires_auth
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
        date = datetime.datetime.utcfromtimestamp(date)
        km = args.get('km')
        works = args.get('works')
        pays = args.get('pays')
        new_note = Notes(car=car_id, date=date, km=km, works=works, pays=pays)
        session_git.add(new_note)
        session_git.commit()
        session_git.close()
        return {'message': 'new note created'}, 201

    @requires_auth
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

    @requires_auth
    def put(self, car_id):
        args = get_arguments_post()
        token = args.get('token')
        users = session_git.query(Users).filter(Users.user_token == token).first()
        note = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.user == users.id, Notes.id == car_id).first()
        if not note:
            return {'message': 'no note with such id'}, 403
        date = args.get('date')
        date = datetime.datetime.utcfromtimestamp(date)
        km = args.get('km')
        works = args.get('works')
        pays = args.get('pays')
        note.date, note.km, note.works, note.pays = date, km, works, pays
        session_git.commit()
        session_git.close()
        return {'message': 'note changed'}, 201


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
