import os
from json import loads

from flask import g
from flask.ext.restless import ProcessingException

from models import User


def postprocess_get_user(result=None, **kw):
    if result['id'] != g.user.id:
        raise ProcessingException(description='Cannot query other users.',
                                  code=405)
    print result


def preprocess_make_user(data=None, **kw):
    if 'username' not in data:
        raise ProcessingException(description='No username provided.',
                                  code=400)

    if User.query.filter(User.username == data['username']).count() != 0:
        raise ProcessingException(description='Username not unique.',
                                  code=400)


def postprocess_make_user(result=None, **kw):
    result = {'id': result['id']}


def preprocess_hazard(data=None, **kw):
    # if anonymity is requested, ensure data is anonymous. Otherwise,
    # associate it with the authenticated user.
    if 'anonymous' not in data or data['anonymous'] == 1:
        data.pop('author_id', None)
    else:
        data['author_id'] = g.user.id

    data.pop('anonymous', None)
    data.pop('photo_id', None)


def postprocess_hazard(result=None, **kw):
    result = {'id': result['id']}
