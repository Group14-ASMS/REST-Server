from flask import request
from flask.ext.restless import ProcessingException

def upload_photo(hazard_id):
    if 'photo' not in request.files:
        raise ProcessingException(description='No photo', code=400)

    print 'File received.'

    return '', 204

