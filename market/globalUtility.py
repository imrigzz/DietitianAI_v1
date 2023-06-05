from market import db, recomend
from market.models import Item,Stats,User
from flask_login import current_user




# user daily calories and nutritional values
def daily_calories():
    # Nutritional values per 2000 calories
    standard_value = [2000,78,0.3,2.3,4.7,275,50,1.4,0.018]
    daily=[]
    # user object
    user_details=User.query.filter(User.id==current_user.id).first()
    if user_details.gender=='M':
        bmr = 88.36 + (13.4 * float(user_details.weight)) + (4.8 * float(user_details.height)) - (5.7 * float(user_details.age))
        tdee = bmr*float(user_details.activity)
        factor = tdee/2000
        for i,items in enumerate(standard_value):
            daily.append(items*factor)
            
    if user_details.gender=='F':
        bmr = 447.6 + (9.2 * float(user_details.weight)) + (3.1 * float(user_details.height)) - (4.3 * float(user_details.age))
        tdee = bmr*float(user_details.activity)
        factor = tdee/2000
        for i,items in enumerate(standard_value):
            daily.append(items*factor)

    return daily
    

#Calories Total_Fat Cholesterol Sodium Potassium Total_Carbohydrates Protein Calcium Iron

def golbal_Nutrient_values():
    global_daily_values = {
        "Calories":2000,
        "Total_Fat":78,
        "Cholesterol":0.3,
        "Sodium":2.3,
        "Potassium":4.7,
        "Total_Carbohydrates":275,
        "Protein":50,
        "Calcium":1.4,
        "Iron":0.018
    }
    return global_daily_values




def update_stats(stats,foods_today_obj,stats_type):
        if stats.first() is None:
            stat_default = Stats(name=stats_type,Calories=0, Total_Fat=0, Cholesterol=0, Sodium=0, Potassium=0, 
                                Total_Carbohydrates=0, Protein=0, Calcium=0, Iron=0, owner=current_user.id)
            db.session.add(stat_default)
            db.session.commit()
        values_list = recomend.update_stats(foods_today_obj)
        stats.first().update_daily_value(values_list)
        return values_list
