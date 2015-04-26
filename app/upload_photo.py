import os

from flask import request, g
from flask.ext.restless import ProcessingException
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from auth import authorized
from models import db, Hazard


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

    return '', 204
