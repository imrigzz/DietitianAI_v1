from scipy import spatial
import pandas as pd
from market.models import Stats
from flask_login import current_user
from sklearn.preprocessing import MinMaxScaler

# https://www.fda.gov/media/135301/download
# calories = 2000g
# fat = 78g
# cholestrol = 300/1000 #less than 300mg = 0.3g
# sodium = 2300/1000 #less than 2300mg = 2.3g
# potassium = 4700/1000 #less than 4700mg = 4.7g
# carbohydrate = 275g
# protein = 50g
# vitamin_d=20Ug
# calcium = 1400mg
# iron =18mg

# 'Calories','Total_Fat','Cholesterol','Sodium','Potassium','Total_Carbohydrates','Protein','vitamin_d','calcium','iron'



#import csv
df = pd.read_csv("market/static/csv/food_nutrition_large.csv")

# Convert milligrams to grams and percentage values to grams
replace = ['Serving_Size','Total_Fat','Cholesterol','Sodium','Potassium','Total_Carbohydrates','Protein','Calcium','Iron']

def remove_notations(df):
    for i in range(0,len(df)):
        for items in replace:
            val = df.loc[i, items]
            if 'mg' in val:
                df.loc[i, items] = float(val.split('mg')[0])/1000
            else:
                df.loc[i, items] = float(val.split('g')[0])

remove_notations(df) 
df = df.set_index('Name')


# ________________Serving type ________________
def serving_ext(food_recognised):
    serving_list={}
    for food in food_recognised:
        if food != "food not found":
            serving_list[food] = (df.loc[food]['serving details'])
    return serving_list




# ________________ UPDATE STATUS ________________
df_status=df.T.copy()
df_status.drop('Serving_Size',inplace=True)
df_status.drop('serving details',inplace=True)

# foods_today_obj = [[chele, 21323, 1], [bahturea, 1341, 2]]
def update_stats(foods_today_obj):
    dv=[0,0,0,0,0,0,0,0,0]
    for food in foods_today_obj:
        for i,values in enumerate(df_status[food.name]):
            dv[i]+=values * food.servings      
    return dv

# ________________ RECOMMENDATIONS ________________

df_100g = df.copy()
for index in df_100g.index:
    multiplier_val = 100/float(df_100g.loc[index,'Serving_Size'])
    for column in df_100g.columns:
        if column == "serving details":
            continue
        else:
            df_100g.loc[index,column]=df_100g.loc[index,column]*multiplier_val
             

df_foods=df_100g.T.copy()
df_foods.drop('Serving_Size',inplace=True)
df_foods.drop('serving details',inplace=True)






# dfx = all foods percentage values
# dfy = percentage still required percentage values

def similar_food(dfx,dfy):
    similarity=[]
    data1 = dfy["Amount_required"]
    for col in dfx.columns:
        data2 = dfx[col]
        result = 1 - spatial.distance.cosine(data1, data2)
        similarity.append(result)
    df_sim = pd.DataFrame(similarity, index=dfx.columns,columns=['Similarity'])
    df_sim=df_sim.sort_values('Similarity', ascending=False)
    return df_sim

# Sort by normalising most required nutrients
# define a custom function to normalize and sort by the sum of required nutrients columns
def sort_by_sum(df,RankNeed):
    # normalize required nutrients columns
    scaler = MinMaxScaler()
    df[[RankNeed[0], RankNeed[1],RankNeed[2]]] = scaler.fit_transform(df[[RankNeed[0], RankNeed[1],RankNeed[2]]])
    print("before weighted")
    print(df[[RankNeed[0], RankNeed[1],RankNeed[2]]])
    # print(df.dtypes)
    # apply weights to each nutrients 50%,30%,20%
    weights = [0.4, 0.35, 0.25]
    df[[RankNeed[0],RankNeed[1],RankNeed[2]]]=df[[RankNeed[0], RankNeed[1], RankNeed[2]]].multiply(weights)
    print()
    print("After weighted")
    print(df[[RankNeed[0], RankNeed[1],RankNeed[2]]])
    # calculate the sum of the normalized 'Age' and 'Salary' columns
    return (df[RankNeed[0]]+df[RankNeed[1]]+df[RankNeed[2]])






# -------------------------------- RECOMMEND FUNCTIONS --------------------------------
def recommendNow(global_daily_values):

    global_weekly_values = []
    global_monthly_values = []
    for items in global_daily_values:
        global_weekly_values.append(items*7)
        global_monthly_values.append(items*31)

    print("Global daily values", global_daily_values)
    print("Global weekly values", global_weekly_values)
    print("Global monthly values", global_monthly_values)

    daily_values = Stats.query.filter(Stats.owner==current_user.id, Stats.name=='daily_values').first()
    weekly_values_Obj = Stats.query.filter(Stats.owner==current_user.id, Stats.name=='weekly_values').first()
    monthly_values_Obj = Stats.query.filter(Stats.owner==current_user.id, Stats.name=='monthly_values').first()

    
    # Nutrients values still required 
    nutrients=['Calories', 'Total_Fat', 'Cholesterol', 'Sodium', 'Potassium',
        'Total_Carbohydrates', 'Protein', 'Calcium', 'Iron']


    daily_required = []
    daily_required.append(global_daily_values[0]-daily_values.Calories)
    daily_required.append(global_daily_values[1]-daily_values.Total_Fat)
    daily_required.append(global_daily_values[2]-daily_values.Cholesterol)
    daily_required.append(global_daily_values[3]-daily_values.Sodium)
    daily_required.append(global_daily_values[4]-daily_values.Potassium)
    daily_required.append(global_daily_values[5]-daily_values.Total_Carbohydrates)
    daily_required.append(global_daily_values[6]-daily_values.Protein)
    daily_required.append(global_daily_values[7]-daily_values.Calcium)
    daily_required.append(global_daily_values[8]-daily_values.Iron)  

    print("______________")
    for items in global_daily_values:
        print(items,type(items))
    print("______________")  
    for items in daily_required:
        print(items,type(items))
    print("______________")

    print(daily_values.Calories)
    print(global_daily_values[0]-daily_values.Total_Fat)
    print("______________")  
  

    weekly_values=[]
    monthly_values=[]
    for item in nutrients:
        weekly_values.append(getattr(weekly_values_Obj, item))
        monthly_values.append(getattr(monthly_values_Obj, item))



    df_daily_required = pd.DataFrame([daily_required])
    df_daily_required.columns=nutrients
    df_daily_required=df_daily_required.T
    df_daily_required.rename(columns = {0:'Amount_required'}, inplace = True)

    df1=similar_food(df_foods,df_daily_required)


    similarityRank =  pd.DataFrame(0,index=df1.index,columns=['Rank'])
    for i,index in enumerate(similarityRank.index):
        similarityRank.loc[index,"Rank"]=i+1

    print("similar foods",similarityRank.index[:10])
    # top 10 foods from cosine similiraty
    df_top_10 = similarityRank.head(10)
    # top 10 food nutritional value df
    df_foods_new = df_foods.T.copy()
    df_new_cosine = df_foods_new.loc[df_foods_new.index.isin(df_top_10.index)].reindex(df_top_10.index)


    #COLLABRATIVE FILTERING
    # Weekly and monthly most required top 3 nutrients
    # find weekly and monthly lacking nutrients
    #find highest still required nutrients
    percentage_weekly = []
    percentage_monthly = []
    for i in range(len(weekly_values)):
        # because cholestrol and sodium are preferred lesser values
        if i==2 or i==3:
            pw = ((global_weekly_values[i]-(weekly_values[i]+(global_weekly_values[i]/2)))/global_weekly_values[i])*100
            pm = ((global_monthly_values[i]-(monthly_values[i]+(global_monthly_values[i]/2)))/global_monthly_values[i])*100
            percentage_weekly.append(pw)
            percentage_monthly.append(pm)
        else:
            pw = ((global_weekly_values[i]-weekly_values[i])/global_weekly_values[i])*100
            pm = ((global_monthly_values[i]-monthly_values[i])/global_monthly_values[i])*100
            percentage_weekly.append(pw)
            percentage_monthly.append(pm)
            

    df_week = pd.DataFrame(percentage_weekly, index=df_foods.index,columns=['PercentRequired'])
    df_week=df_week.sort_values('PercentRequired', ascending=False)

    df_month = pd.DataFrame(percentage_monthly, index=df_foods.index,columns=['PercentRequired'])
    df_month=df_month.sort_values('PercentRequired', ascending=False)
    weekRankNeed = df_week.index[0:3]
    monthRankNeed = df_month.index[0:3]

    print('week and month requirements',weekRankNeed,"\n",monthRankNeed)

    # RANK AFTER MONTH REQQUIREMENTS
    # sort the dataframe by the sum of normalized nutrient required columns using the custom function
    df_new_food_month = df_new_cosine.sort_values(by='Name', key=lambda x: sort_by_sum(df_new_cosine.loc[df_new_cosine.index == x],monthRankNeed), ascending=False)
    
    # top 5 foods from after month requriemnts
    df_new_month = df_new_food_month.head(5)
    # # top 10 food nutritional value df
    df_new_month = df_new_month.loc[df_new_month.index.isin(df_new_month.index)].reindex(df_new_month.index)
    
    # RANK AFTER WEEK REQUIREMENTS
    # sort the dataframe by the sum of normalized nutrient required columns using the custom function
    df_new_food_week = df_new_month.sort_values(by='Name', key=lambda x: sort_by_sum(df_new_month.loc[df_new_month.index == x],weekRankNeed), ascending=False)
    print(df_new_food_week.index[0:3])

    return  df_new_food_week.index[0:3]



        

