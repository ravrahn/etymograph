# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import model
from web import web
from api import api
from edit import edit
from user import user, user_area

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

app.register_blueprint(web)
app.register_blueprint(api)
app.register_blueprint(edit)
app.register_blueprint(user)

app.jinja_env.globals.update(user_area=user_area)


if __name__ == '__main__':
    app.run(debug=True)
