# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from helpers import *
import model
from web import web
from api import api
from edit import edit
from user import user, user_area

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

app.register_blueprint(web)
app.register_blueprint(edit)
app.register_blueprint(user)
app.register_blueprint(api, url_prefix='/api')

app.jinja_env.globals.update(user_area=user_area)

@app.errorhandler(404)
@app.errorhandler(400)
def error(err):
    return render_search_template('error.html', error_code=err.code, error_message=err.description, title='Error')


if __name__ == '__main__':
    app.run(debug=True)
