import os

from flask import request, g
from flask.ext.restless import ProcessingException
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from auth import authorized
from models import db, Hazard
from . import app


def s3_upload(name, fileobj):
    conn = S3Connection(app.config['AWS_ACCESS_ID'],
                        app.config['AWS_SECRET_KEY'],
                        host='s3-us-west-2.amazonaws.com')

    bucket = conn.get_bucket(app.config['AWS_S3_BUCKET'])

    key = Key(bucket)
    key.key = name
    key.set_contents_from_file(fileobj)


@authorized
def upload_photo(hazard_id):
    if 'photo' not in request.files:
        raise ProcessingException(description='No photo', code=400)

    # get hazard by id
    try:
        hazard = Hazard.query \
            .options(joinedload(Hazard.user)) \
            .filter(Hazard.id == hazard_id).one()
    except NoResultFound:
        raise ProcessingException(description='No hazard matching id.',
                                  code=400)
    except MultipleResultsFound:
        raise ProcessingException(description='Server state inconsistent.',
                                  code=500)

    # ensure user owns hazard
    if hazard.user.id != g.user.id:
        raise ProcessingException(description='User does not own hazard',
                                  code=401)

    # set photo_id to hazard id + random string
    hid = '{:011d}'.format(hazard_id)
    rand = ''.join('{:02x}'.format(ord(x)) for x in os.urandom(16))

    hazard.photo_id = hid + rand
    db.session.commit()

    name = hazard.photo_id + '.jpg'
    s3_upload(name, request.files['photo'])

    return '', 204
