from uuid import uuid4

from flask import request, jsonify, g
from flask.ext.restless import ProcessingException
from passlib.hash import bcrypt
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import db, User


def process_new_user(data=None, **kw):
    if 'password' not in data:
        raise ProcessingException(description='No password.', code=400)

    password = data['password']
    data['hashed_password'] = bcrypt.encrypt(password,
                                      rounds=12,
                                      ident='2y')
    del data['password']


def disallowed(reason):
    def method(*args, **kwargs):
        raise ProcessingException(description=reason, code=405)

    return method


def is_authorized(*args, **kwargs):
    if 'token' not in request.args:
        raise ProcessingException(description='No token or user id.', code=400)

    token = request.args['token']

    try:
        user = User.query.filter(User.token == token).one()
    except NoResultFound:
        raise ProcessingException(description='Bad authentication.', code=401)
    except MultipleResultsFound:
        raise ProcessingException(description='Server state inconsistent.',
                                  code=500)

    # log this user in for the remainder of the request
    g.user = user


def login():
    if not all(x in request.args for x in ['username', 'password']):
        raise ProcessingException(description='No username or password.',
                                  code=400)

    username = request.args['username']
    password = request.args['password']

    # generate a token
    token = uuid4().hex

    try:
        user = User.query.filter(User.username == username).one()

        if not bcrypt.verify(password, user.hashed_password):
            raise ProcessingException(description='Bad authentication.',
                                      code=401)
    except NoResultFound:
        raise ProcessingException(description='No user found.', code=400)
    except MultipleResultsFound:
        raise ProcessingException(description='Server state inconsistent.',
                                  code=500)

    # update token
    user.token = token
    db.session.commit()

    return jsonify(id=user.id, token=user.token)
