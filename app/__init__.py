from os import environ

from flask import Flask
from flask.ext.restless import APIManager

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
manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(models.User, methods=['GET', 'POST'])
manager.create_api(models.Hazard, methods=['GET', 'POST'])
