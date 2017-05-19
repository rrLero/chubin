# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from my_models import Base, Cars
import os


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
    parser.add_argument('gov_number', type=str, location='json', required=True, help="Что то не так заполнено в гос номере")
    parser.add_argument('car_type', type=str, location='json', required=True, help="Что то не так заполнено в тип машины")
    parser.add_argument('gov_number_trailer', type=str, location='json', help="Что то не так заполнено в прицеп")
    parser.add_argument('user_id', type=int, location='json', help="User")

    return parser.parse_args()


def get_arguments_del():
    parser2.add_argument('id_list', type=list, required=True, location='json', help="id_list - не пришел")
    return parser2.parse_args()


# запрос для Python консоли - просто скопировать в консоль
# import requests
# x = requests.post('http://0.0.0.0:5000/', json = {'test': '1', 'test2': 2, 'test3': 3, 'test4': 4, 'test5': [1,2,3]})


class GetAddEditCars(Resource):
    def get(self):
        query = session_git.query(Cars)
        car_list = [{'gov_number': car.gov_number, 'car_type': car.car_type,
                     'gov_number_trailer': car.gov_number_trailer, 'id': car.id, 'user_id': car.user} for car in query]
        session_git.close()
        return jsonify(car_list)

    def post(self):
        args = get_arguments_post()
        gov_number = args.get('gov_number')
        car_type = args.get('car_type')
        gov_number_trailer = args.get('gov_number_trailer')
        user = args.get('user_id')
        new_car = Cars(gov_number=gov_number, car_type=car_type, gov_number_trailer=gov_number_trailer, user=user)
        session_git.add(new_car)
        session_git.commit()
        session_git.close()
        return {'message': 'new car created'}, 201

    def delete(self):
        args_del = get_arguments_del()
        id_car = args_del.get('id_list')
        query = session_git.query(Cars)
        for car in query:
            if car.id in id_car:
                session_git.delete(car)
        session_git.commit()
        session_git.close()
        return {'message': 'car deleted by list'}, 202