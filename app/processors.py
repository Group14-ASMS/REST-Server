import os

from json import loads

from flask import g
from flask.ext.restless import ProcessingException


def postprocess_get_user(result=None, **kw):
    if result['id'] != g.user.id:
        return ProcessingException(
            description='Cannot query other users.',
            code='405')
    print result


def postprocess_make_user(result=None, **kw):
    result = {'id': result['id']}


def preprocess_hazard(data=None, **kwargs):
    # if anonymity is requested, ensure data is anonymous. Otherwise,
    # associate it with the authenticated user.
    if data['anonymous'] == 1:
        data['author_id'] = 0
    else:
        data['author_id'] = g.user.id

    data.pop('photo_id', None)


def postprocess_hazard(result=None, **kw):
    result = {'id': result['id']}
