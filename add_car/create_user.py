# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from my_models import Base, Users
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
    parser.add_argument('user_name', type=str, location='json', required=True, help="Что то не так заполнено в user_name")
    parser.add_argument('password', type=str, location='json', required=True, help="Что то не так заполнено в Password")
    return parser.parse_args()


def get_arguments_del():
    parser2.add_argument('id_user', type=int, required=True, location='json', help="id_user - не пришел")
    return parser2.parse_args()


# запрос для Python консоли - просто скопировать в консоль
# import requests
# x = requests.post('http://0.0.0.0:5000/', json = {'test': '1', 'test2': 2, 'test3': 3, 'test4': 4, 'test5': [1,2,3]})


class CreateUser(Resource):
    def get(self):
        query = session_git.query(Users)
        users_list = [{'user_name': user.user_name, 'password': user.user_password, 'id': user.id} for user in query]
        session_git.close()
        return jsonify(users_list)

    def post(self):
        args = get_arguments_post()
        user_name = args.get('user_name')
        password = args.get('password')
        new_user = Users(user_name=user_name, user_password=password)
        session_git.add(new_user)
        session_git.commit()
        session_git.close()
        return {'message': 'new user created'}, 201

    def delete(self):
        args_del = get_arguments_del()
        id_user = args_del.get('id_user')
        query = session_git.query(Users)
        for user in query:
            if user.id in id_user:
                session_git.delete(user)
        session_git.commit()
        session_git.close()
        return {'message': 'user deleted'}, 202