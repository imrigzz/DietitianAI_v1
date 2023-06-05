# CREATE A DATABASE RUN ONCE

from market import app
from market.models import db,Item
app.app_context().push()
db.create_all()






