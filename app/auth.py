from uuid import uuid4

from flask import request, jsonify
from flask.ext.restless import ProcessingException
from passlib.hash import pbkdf2_sha512
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import db, User

def is_authorized(*args, **kwargs):
    if not all(x in request.args for x in ['token', 'user']):
        raise ProcessingException(description='Bad request.', code=400)

    user_id = request.args['user']
    token = request.args['token']

    try:
        User.query.filter(User.id == user_id) \
            .filter(User.token == token) \
            .one()
    except NoResultFound:
        raise ProcessingException(description='Bad authentication.', code=401)
    except MultipleResultsFound:
        raise ProcessingException(description='Server state inconsistent.', code=500)

def login():
    if not all(x in request.args for x in ['username', 'password']):
        raise ProcessingException(description='Bad request.', code=400)

    username = request.args['username']
    password = request.args['password']

    # get the password hash to test against the database
    passhash = pbkdf2_sha512(password, salt_size=16, rounds=8000)

    # generate a token
    token = uuid4()

    try:
        user = User.query.filter(User.username == username) \
            .filter(User.passhash == passhash) \
            .one()
    except NoResultFound:
        raise ProcessingException(description='Bad authentication.', code=401)
    except MultipleResultsFound:
        raise ProcessingException(description='Server state inconsistent.', code=500)

    # update token
    user.token = token
    db.session.commit()

    return jsonify(id=user.id, token=user.token)
