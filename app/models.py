from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)


class Category(BaseModel):
    __tablename__ = 'categories'

    name = db.Column(db.String(50), nullable=False)
    hazards = db.relationship('Hazard', backref='category')


class Hazard(BaseModel):
    __tablename__ = 'hazards'

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    time = db.Column(db.DateTime, nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    cat = db.Column(db.Integer, db.ForeignKey('categories.id'))
    anonymous = db.Column(db.Boolean, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    info = db.Column(db.String(4000), nullable=False)
    photo_id = db.Column(db.String(43), nullable=True)
    archived = db.Column(db.Boolean, nullable=False, default=False)

class User(BaseModel):
    __tablename__ = 'users'

    name = db.Column(db.String(250), nullable=False, unique=True)
    username = db.Column(db.String(32), nullable=False)
    clearance = db.Column(db.Integer, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(32))
    hazards = db.relationship('Hazard',
                              backref=db.backref('user', lazy='joined'))
