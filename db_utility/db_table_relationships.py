# RELATIONSHIPS
from market import app
from market.models import db,Item,User
app.app_context().push()

# item1=Item.query.filter_by(name='samsung galaxys20').first()  #select item name
# item1.owner = User.query.filter_by(username='achuk').first().id
# db.session.add(item1)
# db.session.commit()

i = Item.query.filter_by(name ='Iphone 14').first()
print(i.owned_user.username)