from json import dumps, loads
from datetime import datetime
from urlparse import urlparse

from passlib.hash import pbkdf2_sha512

from app import app, db
from app.models import Category

user_alex = {
    'name': 'Alex',
    'username': 'alex',
    'passhash': pbkdf2_sha512.encrypt('hello', salt_size=16, rounds=8000),
    'clearance': 0
}

hazard_bag = {
    'author_id': 1,
    'time': datetime.utcnow().isoformat(),
    'x': 0.0,
    'y': 0.0,
    'cat': 1,
    'anonymous': 0,
    'priority': 1,
    'info': 'blah',
    'photo_id': 1
}

hazard_anon_bag = {
    'author_id': 0,
    'time': datetime.utcnow().isoformat(),
    'x':  5.0,
    'y': -5.0,
    'cat': 1,
    'anonymous': 1,
    'priority': 1,
    'info': 'foo bar',
    'photo_id': 1
}

def make_category():
    cat_baggage = Category(name='unattended baggage')

def make_user(client, user_dict):
    resp = client.post('/api/users',
        content_type='application/json',
        data=dumps(user_dict))

    return urlparse(resp.headers['Location']).path

def make_hazard(client, hazard_dict):
    resp = client.post('/api/hazards',
        content_type='application/json',
        data=dumps(hazard_dict))

    return urlparse(resp.headers['Location']).path

def setup_module(module):
    module.app.config['TESTING'] = True

class TestApp(object):
    def setup(self):
        self.app = app.test_client()

    def setup_method(self, method):
        db.create_all()

    def teardown_method(self, method):
        db.drop_all()

    def test_get_many_empty(self):
        resp = self.app.get('/api/users')
        data = loads(resp.data)
        assert data == {
            'num_results': 0,
            'objects': [],
            'page': 1,
            'total_pages': 0
        }

    def test_make_new_cat(self):
        make_category()

    def test_make_new_user(self):
        path = make_user(self.app, user_alex)

        resp = self.app.get(path)
        data = loads(resp.data)

        anticipated = {'id': 1, 'hazards': [], 'token': None}
        anticipated.update(user_alex)

        assert data == anticipated

    def test_make_new_hazard(self):
        make_category()
        make_user(self.app, user_alex)
        path = make_hazard(self.app, hazard_bag)

        resp = self.app.get(path)
        data = loads(resp.data)

        user = {'id': 1, 'token': None}
        user.update(user_alex)

        anticipated = {'id': 1, 'user': user}
        anticipated.update(hazard_bag)

        assert data == anticipated

    def test_make_anon_hazard(self):
        make_category()
        path = make_hazard(self.app, hazard_bag)

        resp = self.app.get(path)
        data = loads(resp.data)

        anticipated = {'id': 1, 'user': None}
        anticipated.update(hazard_bag)

        assert data == anticipated
