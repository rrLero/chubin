# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource
from my_models import Cars, Users, Notes, session_git
from random import choice
from string import ascii_letters


parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()


def get_arguments_post():
    parser.add_argument('user_name', type=str, required=True, help="нет имени пользователя")
    parser.add_argument('password', type=str, required=True, help="нет пароля")
    return parser.parse_args()


class GetToken(Resource):
    def post(self):
        args = get_arguments_post()
        user_name = args.get('user_name')
        password = args.get('password')
        user_query = session_git.query(Users).filter(Users.user_name == user_name.lower(), Users.user_password == password).first()
        if not user_query:
            session_git.close()
            return {'message': 'unauthorized'}, 401
        token = ''.join(choice(ascii_letters) for i in range(17))
        user_query.user_token = token
        session_git.commit()
        session_git.close()
        return {'token': token}, 200