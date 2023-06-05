# WORK WITH DATABASE : 
# 1 :  INSERT
from market import app
from market.models import db,Item,User,Stats
app.app_context().push()
from datetime import date,datetime,timezone
from sqlalchemy import func


# USER TABLE
# u1 = User(username="achuk", password_hash="12312412421", email_address="rizin@gmail.com")
# db.session.add(u1)
# db.session.commit()

# ITEM TABLE
# consumed_date = date(2021,2,22)
# consumed_datetime = datetime.now()
# item3 = Stats(
#     name = "daily_values", 
#     Calories = 0,
#     Total_Fat = 0,
#     Cholesterol = 0,
#     Sodium = 0,
#     Potassium = 0,
#     Total_Carbohydrates = 0,
#     Protein = 0,
#     Calcium = 0,
#     Iron = 0,
#     owner = 1
#     )
# db.session.add(item3)
# db.session.commit()




