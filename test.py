from json import dumps, loads
from datetime import datetime
from urlparse import urlparse

from app import app, db
from app.models import Category, Hazard

user_alex = {
    'name': 'Alex',
    'username': 'alex',
    'password': 'hello',
    'clearance': 0
}

user_lucas = {
    'name': 'Lucas',
    'username': 'lucas',
    'password': 'world',
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
    'title': 'oh no!',
    'info': 'blah',
    'photo_id': 'aebcafe'
}

hazard_anon_bag = {
    'author_id': 0,
    'time': datetime.utcnow().isoformat(),
    'x':  5.0,
    'y': -5.0,
    'cat': 1,
    'anonymous': 1,
    'priority': 1,
    'title': 'spam eggs',
    'info': 'foo bar',
    'photo_id': 'a12345'
}


def post_json_notoken(client, path, data):
    return client.post(path,
                       content_type='application/json',
                       data=dumps(data))


def post_json(client, path, token, data):
    return client.post(path,
                       content_type='application/json',
                       query_string={'token': token},
                       data=dumps(data))


def get_params(client, path, params):
    return client.get(path,
                      query_string=params)


def make_user(client, user):
    return post_json_notoken(client, '/api/users', user)


def make_hazard(client, token, hazard):
    return post_json(client, '/api/hazards', token, hazard)


def submit_photo(client, token, hazard_id, fileobj):
    return client.post('api/hazards/{}/photo'.format(hazard_id),
                       query_string={'token': token},
                       data={'photo': fileobj})


def login(client, creds):
    return get_params(client, '/api/login', creds)


class TestSimple(object):
    def setup(self):
        self.app = app.test_client()

    def setup_method(self, method):
        db.create_all()

        cat = Category(name='test')
        db.session.add(cat)
        db.session.commit()

    def teardown_method(self, method):
        db.session.close()
        db.drop_all()

    def test_make_user(self):
        # create new user
        resp = make_user(self.app, user_alex)

        assert resp.status == '201 CREATED'
        assert loads(resp.data)['id'] == 1

    def test_login(self):
        make_user(self.app, user_alex)

        # login
        resp = login(self.app, {'username': 'alex', 'password': 'hello'})

        assert resp.status == '200 OK'
        assert loads(resp.data)['id'] == 1

    def test_make_hazard(self):
        make_user(self.app, user_alex)
        resp = login(self.app, {'username': 'alex', 'password': 'hello'})
        token = loads(resp.data)['token']

        # create new hazard
        resp = make_hazard(self.app, token, hazard_bag)

        assert resp.status == '201 CREATED'
        assert loads(resp.data)['id'] == 1

        hazard = Hazard.query.filter(Hazard.id == 1).one()

        assert hazard.photo_id is None

    def test_make_anon_hazard(self):
        make_user(self.app, user_alex)
        resp = login(self.app, {'username': 'alex', 'password': 'hello'})
        token = loads(resp.data)['token']

        # create new anonymous hazard
        resp = make_hazard(self.app, token, hazard_anon_bag)

        assert resp.status == '201 CREATED'
        assert loads(resp.data)['id'] == 1

        hazard = Hazard.query.filter(Hazard.id == 1).one()

        assert hazard.photo_id is None

    def test_make_hazard_with_photo(self):
        make_user(self.app, user_alex)
        resp = login(self.app, {'username': 'alex', 'password': 'hello'})
        token = loads(resp.data)['token']
        make_hazard(self.app, token, hazard_bag)

        with open('s3conn/testimage.jpg') as f:
            resp = submit_photo(self.app,
                                token,
                                1,
                                (f, 'example.jpg'))

        assert resp.status == '204 NO CONTENT'

        hazard = Hazard.query.filter(Hazard.id == 1).one()

        assert hazard.photo_id is not None
        assert len(hazard.photo_id) == 43


class TestRejections(object):
    def setup(self):
        self.app = app.test_client()

    def setup_method(self, method):
        db.create_all()

    def teardown_method(self, method):
        db.drop_all()

    def test_no_get_many(self):
        make_user(self.app, user_alex)
        make_user(self.app, user_lucas)
        resp = login(self.app, {'username': 'alex', 'password': 'hello'})
        token = loads(resp.data)['token']

        resp = get_params(self.app, '/api/users', {'token': token})

        assert resp.status == '405 METHOD NOT ALLOWED'

    def test_no_respond_no_token(self):
        # user route tests
        assert get_params(self.app, '/api/users/1', {}).status == '400 BAD REQUEST'
        assert post_json_notoken(self.app, '/api/users', {}).status == '400 BAD REQUEST'

    def test_make_non_unique_user(self):
        make_user(self.app, user_alex)

        # make the user with the same name
        resp = make_user(self.app, user_alex)

        assert resp.status == '400 BAD REQUEST'
