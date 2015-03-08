from flask import Flask
from flask.ext.restless import APIManager
from models import db

app = Flask(__name__)
app.config.from_object('debug')

# add the database
db.app = app
db.init_app(app)

if app.config['DEBUG']:
    db.create_all()

manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(models.User, methods=['GET', 'POST', 'DELETE'])
