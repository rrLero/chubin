# -*- coding: utf-8 -*-
from flask_restful import reqparse, Resource, request
from flask import jsonify
from my_models import Users, session_git, Cars, Notes


parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()


def get_arguments_post():
    parser.add_argument('user_name', type=str, location='json', required=True, help="Что то не так заполнено в user_name")
    parser.add_argument('password', type=str, location='json', required=True, help="Что то не так заполнено в Password")
    return parser.parse_args()


def get_arguments_del():
    parser2.add_argument('id_user', type=int, required=True, location='json', help="id_user - не пришел")
    parser2.add_argument('password_for_del', type=int, required=True, location='json', help="id_user - не пришел")
    return parser2.parse_args()


class CreateUser(Resource):
    def get(self):
        query = session_git.query(Users)
        users_list = [{'user_name': user.user_name, 'id': user.id, 'password': user.user_password, 'token': user.user_token} for user in query]
        # users_list = [
        #     {'user_name': user.user_name, 'id': user.id} for
        #     user in query]
        session_git.close()
        return jsonify(users_list)

    def post(self):
        args = get_arguments_post()
        user_name = args.get('user_name')
        password = args.get('password')
        user = session_git.query(Users).filter(Users.user_name == user_name.lower()).first()
        if user:
            return {'message': 'user with such login already in base try another name'}, 400
        new_user = Users(user_name=user_name.lower(), user_password=password)
        session_git.add(new_user)
        session_git.commit()
        session_git.close()
        return {'message': 'new user created'}, 201

    # def delete(self):
    #     args_del = get_arguments_del()
    #     id_user = args_del.get('id_user')
    #     password_for_del
    #     query = session_git.query(Users)
    #     for user in query:
    #         if user.id == id_user:
    #             cars = session_git.query(Cars).join(Cars, Users.lnk_users_cars).filter(Users.id == id_user)
    #             for car in cars:
    #                 notes = session_git.query(Notes).join(Notes, Cars.lnk_cars_notes).filter(Cars.id == car.id)
    #                 for note in notes:
    #                     session_git.delete(note)
    #                 session_git.delete(car)
    #             session_git.delete(user)
    #     session_git.commit()
    #     session_git.close()
    #     return {'message': 'user deleted'}, 201