# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_restful import Api
from add_car.add_car import GetAddEditCars
from add_car.create_user import CreateUser

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
api = Api(app)


@app.route('/')
def index():
    return 'Test app Postgresql on Heroku'

# Добавить запись в базу в таблицу Cars
api.add_resource(GetAddEditCars, '/car')
api.add_resource(CreateUser, '/user')
# api.add_resource(Get)


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# if __name__ == '__main__':
#     app.run(debug=True)