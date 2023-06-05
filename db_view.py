# 3 : PRINT DATABASE
from market import app
from market.models import db,Item
app.app_context().push()
for item in Item.query.all():
    print(item.id,' ',item.name,' ',item.price,' ',item.barcode,' ',item.description)

# 2 : CHECK FILTERED VIEW
# for item in Item.query.filter_by(price=100000):
#     print(item.id,' ',item.name,' ',item.price,' ',item.barcode,' ',item.description)


# 3 : CHECK ITEM present in database
# from market import app,Item,db
# app.app_context().push()
# print(Item.query.all())



