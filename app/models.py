from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)


class Category(BaseModel):
    __tablename__ = 'categories'

    name = db.Column(db.String(50), nullable=False)


class Hazard(BaseModel):
    __tablename__ = 'hazards'

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.DateTime, nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    cat = db.Column(db.Integer, db.ForeignKey('categories.id'))
    anonymous = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    info = db.Column(db.String(4000), nullable=False)
    photo_id = db.Column(db.Integer, nullable=False)


class User(BaseModel):
    __tablename__ = 'users'

    name      = db.Column(db.String(250), nullable=False)
    clearance = db.Column(db.Integer, nullable=False)
    hazards   = db.relationship('Hazard', backref='user')
