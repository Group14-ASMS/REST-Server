from uuid import uuid4

from flask import request, jsonify
from flask.ext.restless import ProcessingException
from passlib.hash import pbkdf2_sha512
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import db, User

def process_new_user(data=None, **kw):
    if 'password' not in data:
        raise ProcessingException(description='No password.', code=400)

    password = data['password']
    data['passhash'] = pbkdf2_sha512.encrypt(password, salt_size=16, rounds=8000)
    del data['password']

def is_authorized(*args, **kwargs):
    if not all(x in request.args for x in ['token', 'user']):
        assert 0
        raise ProcessingException(description='No token or user id.', code=400)

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
        raise ProcessingException(description='No username or password.', code=400)

    username = request.args['username']
    password = request.args['password']

    # generate a token
    token = uuid4().hex

    try:
        user = User.query.filter(User.username == username) \
            .one()

        if not pbkdf2_sha512.verify(password, user.passhash):
            raise ProcessingException(description='Bad authentication.', code=401)
    except NoResultFound:
        raise ProcessingException(description='No user found.', code=400)
    except MultipleResultsFound:
        raise ProcessingException(description='Server state inconsistent.', code=500)

    # update token
    user.token = token
    db.session.commit()

    return jsonify(id=user.id, token=user.token)
