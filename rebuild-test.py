from app import db
from app.models import Category

print "Targeting table {}".format(db.engine)

print "Clearing tables..."
db.drop_all()
db.create_all()

print "Adding test category..."
cat = Category(name='test')
db.session.add(cat)
db.session.commit()

print "Done!"

