# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from my_models import Cars, Users, Notes, session_git
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
    parser.add_argument('gov_number', type=str, location='json', required=True, help="Что то не так заполнено в гос номере")
    parser.add_argument('car_type', type=str, location='json', required=True, help="Что то не так заполнено в тип машины")
    parser.add_argument('gov_number_trailer', type=str, location='json', help="Что то не так заполнено в прицеп")
    parser.add_argument('token', help="token")
    return parser.parse_args()


# запрос для Python консоли - просто скопировать в консоль
# import requests
# x = requests.post('http://0.0.0.0:5000/', json = {'test': '1', 'test2': 2, 'test3': 3, 'test4': 4, 'test5': [1,2,3]})


class GetAddEditCars(Resource):
    @requires_auth
    def get(self):
        args = get_arguments_get()
        token = args.get('token')
        user_query = session_git.query(Users).filter(Users.user_token == token).first()
        user_id = user_query.id
        if not user_query:
            return 'Page no found', 404
        query = session_git.query(Cars).join(Cars, Users.lnk_users_cars).filter(Cars.user == user_id)
        car_list = [{'gov_number': car.gov_number, 'car_type': car.car_type,
                     'gov_number_trailer': car.gov_number_trailer, 'id': car.id, 'user_id': user_id} for car in query]
        session_git.close()
        return jsonify(car_list)

    def post(self):
        args = get_arguments_post()
        gov_number = args.get('gov_number')
        car_type = args.get('car_type')
        gov_number_trailer = args.get('gov_number_trailer')
        token = args.get('token')
        users = session_git.query(Users).filter(Users.user_token == token).first()
        user = users.id
        if not users:
            return {'message': 'no user with such id'}, 401
        new_car = Cars(gov_number=gov_number, car_type=car_type, gov_number_trailer=gov_number_trailer, user=user)
        session_git.add(new_car)
        session_git.commit()
        session_git.close()
        return {'message': 'new car created'}, 201

    def delete(self, car_id):
        args = get_arguments_get()
        token = args.get('token')
        users = session_git.query(Users).filter(Users.user_token == token).first()
        user_id = users.id
        id_car = car_id
        query = session_git.query(Cars).join(Cars, Users.lnk_users_cars).filter(Cars.user == user_id)
        for car in query:
            if car.id == id_car:
                query_notes = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.id == id_car)
                for note in query_notes:
                    session_git.delete(note)
                session_git.delete(car)
                session_git.commit()
                session_git.close()
                return {'message': 'car deleted by list'}, 202
        session_git.close()
        return {'message': 'error'}, 401
