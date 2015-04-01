from json import dumps, loads
from datetime import datetime
from urlparse import urlparse

from app import app, db
from app.models import Category, User

user_alex = {
    'name': 'Alex',
    'username': 'alex',
    'password': 'hello',
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

def post_json_notoken(client, path, data):
    return client.post(path,
        content_type='application/json',
        data=dumps(data))


def post_json(client, path, token, id, data):
    return client.post(path,
        content_type='application/json',
        query_string={'token': token, 'user': id},
        data=dumps(data))


def get_params(client, path, params):
    return client.get(path,
        query_string=params)


class TestLoggedIn(object):
    def make_user(self, user):
        return post_json_notoken(self.app, '/api/users', user)

    def make_hazard(self, token, id, hazard):
        return post_json(self.app, '/api/hazards', token, id, hazard)

    def login(self, creds):
        return get_params(self.app, '/api/login', {'username': 'alex', 'password': 'hello'})

    def setup(self):
        self.app = app.test_client()

    def setup_method(self, method):
        db.create_all()

    def teardown_method(self, method):
        db.drop_all()

    def test_make_user(self):
        # create new user
        resp = self.make_user(user_alex)

        assert resp.status == '201 CREATED'
        assert loads(resp.data)['id'] == 1

    def test_login(self):
        self.make_user(user_alex)

        # login
        resp = self.login({'username': 'alex', 'password': 'hello'})

        assert resp.status == '200 OK'
        assert loads(resp.data)['id'] == 1

    def test_make_hazard(self):
        self.make_user(user_alex)
        token = loads(self.login(user_alex).data)['token']

        # create new hazard
        resp = self.make_hazard(token, 1, hazard_bag)

        assert resp.status == '201 CREATED'
        assert loads(resp.data)['id'] == 1

    