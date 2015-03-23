from os import environ

from flask import Flask
from flask.ext.restless import APIManager

from auth import login, is_authorized
from models import db

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

preprocessor_verbs = ['GET_SINGLE', 'GET_MANY', 'POST']
preprocessors = dict((k, [is_authorized]) for k in preprocessor_verbs)

manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(models.User, methods=['GET', 'POST'], preprocessors=preprocessors)
manager.create_api(models.Hazard, methods=['GET', 'POST'], preprocessors=preprocessors)
