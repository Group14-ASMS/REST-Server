from os import environ

from flask import Flask
from flask.ext.restless import APIManager

from auth import process_new_user, disallowed, is_authorized, login
from models import db
from preprocessors import *

app = Flask(__name__)

# conditional configuration
if 'ASMS_CONFIG' in environ:
    app.config.from_envvar('ASMS_CONFIG')
else:
    app.config.from_pyfile('debug.cfg')

# add the database
db.app = app
db.init_app(app)

if app.config['DEBUG']:
    db.create_all()

# routes
app.add_url_rule('/api/login', 'login', login)

manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(models.User,
                   methods=['GET', 'POST'],
                   preprocessors={
                       'GET_SINGLE': [is_authorized],
                       'GET_MANY': [disallowed('Method not allowed.')],
                       'POST': [process_new_user]
                   },
                   postprocessors={
                       'GET_SINGLE': [postprocess_get_user],
                       'POST': [postprocess_make_user]
                   })
manager.create_api(models.Hazard,
                   methods=['GET', 'POST'],
                   preprocessors={
                       'GET_SINGLE': [is_authorized],
                       'GET_MANY': [is_authorized],
                       'POST': [is_authorized, preprocess_hazard]
                   })
