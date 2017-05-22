# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_restful import Api
from add_car.add_car import GetAddEditCars
from add_car.create_user import CreateUser
from add_car.notes import CreateEditDeleteNotes
from add_car.statistics import ShowCars
from add_car.login import GetToken
from flask_cors import CORS, cross_origin

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)
api = Api(app)


@app.route('/')
def index():
    return 'APP FOR CARS STATISTIC'

# работа с таблицу Cars
api.add_resource(GetAddEditCars, '/car', '/car/<int:car_id>')
# работа с таблицу Users
api.add_resource(CreateUser, '/user')
# работа с таблицу Notes
api.add_resource(CreateEditDeleteNotes, '/notes', '/notes/<int:car_id>')
# получение статистики по базе данных
api.add_resource(ShowCars, '/<int:user_id>/statistics/<id_car>')
# Login
api.add_resource(GetToken, '/get_token')


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
