from market import app, recomend
from flask import render_template,redirect, url_for, flash, request
from market.models import Item,User,Upload,Stats
from market.forms import RegisterForm, LoginForm
from market import db, recogniseFood, recomend
from flask_login import login_user,logout_user, login_required, current_user
from datetime import date,datetime,timezone
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import date,datetime,timezone
from sqlalchemy import func, desc, DATE
import os, json
import urllib.request
import pandas as pd
from market.globalUtility import golbal_Nutrient_values, update_stats, daily_calories
import jinja2

# create the environment object and update the global variables





# ################ HOME ##########################



@app.route("/")
@app.route("/home")
def home_page():
    if current_user.is_authenticated:
        count = Item.query.filter_by(owner=current_user.id).count()
        return render_template('home.html',count=count)
    else:
        return render_template('home.html')



################## MAIN ########################
@app.route("/market")
@login_required
def food_page():
    count = Item.query.filter_by(owner=current_user.id).count()
    items = Item.query.filter_by(owner=current_user.id).order_by(desc(Item.datetime_posted)).all()
    # for daily calories fat and protein
    nutrientChart = Stats.query.filter_by(owner=current_user.id).first()
    if nutrientChart is None:
        chartCon = [0,0,0]
    else:
        chartCon = [nutrientChart.Calories,nutrientChart.Total_Fat, nutrientChart.Protein]  #list
    NutrientChartReq = golbal_Nutrient_values()
    chartReq = [NutrientChartReq['Calories'],NutrientChartReq['Total_Fat'],NutrientChartReq['Protein']]

    # daily
    stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
    foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
    daily_values_list=update_stats(stats_daily,foods_today_obj,'daily_values')
        
        
    # update weekely
    stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
    current_week_number = datetime.now().isocalendar()[1]
    records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
    weekly_values_list=update_stats(stats_weekly,records,'weekly_values')

    # monthly
    stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
    current_month_number = datetime.now().month
    records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
    monthly_values_list=update_stats(stats_monthly,records,'monthly_values')
    serving_ext={}
    return render_template('market.html', items=items, chartCons=chartCon, chartReqs=chartReq, count=count, serving_ext=serving_ext,
                           daily_values_list=daily_values_list,weekly_values_list=weekly_values_list,monthly_values_list=monthly_values_list)


# Route to upload meal image 
@app.route('/market', methods=['POST','GET'])
def food_added():
    show_modal = True  # set this variable to True to display the modal
    count = Item.query.filter_by(owner=current_user.id).count()
    items = Item.query.filter_by(owner=current_user.id).order_by(desc(Item.datetime_posted)).all()

    # daily
    stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
    foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
    daily_values_list=update_stats(stats_daily,foods_today_obj,'daily_values')
        
        
    # update weekely
    stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
    current_week_number = datetime.now().isocalendar()[1]
    records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
    weekly_values_list=update_stats(stats_weekly,records,'weekly_values')

    # monthly
    stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
    current_month_number = datetime.now().month
    records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
    monthly_values_list=update_stats(stats_monthly,records,'monthly_values')
    
    # for daily calories fat and protein
    nutrientChart = Stats.query.filter_by(owner=current_user.id).first()
    if nutrientChart is None:
        chartCon = [0,0,0]
    else:
        chartCon = [nutrientChart.Calories,nutrientChart.Total_Fat, nutrientChart.Protein]  #list
    NutrientChartReq = golbal_Nutrient_values()
    chartReq = [NutrientChartReq['Calories'],NutrientChartReq['Total_Fat'],NutrientChartReq['Protein']]


    
    # Get add food to database part
    if request.form['submitAction']=='addToDB':
        recent_food_object = Upload.query.filter(Upload.addflag==1).all()
        recent_food = recent_food_object
        food_recognised = recogniseFood.recogniseFood(recent_food)
        mealtype = request.form['meal-type']
        my_datetime_str = ""
        data = mealtype+'*'+my_datetime_str
        not_found_count=0
        for food in food_recognised:
            if food=="food not found":
                not_found_count+=1
            else:
                data+='*'
                data+=food
        serving_ext = recomend.serving_ext(food_recognised)
        if not_found_count>0:
            flash(f'{not_found_count}: Food are not supported yet, Please check food list for supported foods',category='danger')
        return render_template('market.html', items=items, chartCons=chartCon, chartReqs=chartReq, count=count, show_modal=show_modal, data=data,
                                food_recognised=food_recognised, serving_ext=serving_ext)
    
    # add food to database Previous part
    if request.form['submitAction']=='addToDBP':
        recent_food_object = Upload.query.filter(Upload.addflag==1).all()
        recent_food = recent_food_object
        food_recognised = recogniseFood.recogniseFood(recent_food)
        food_date = request.form['food_date']
        food_time = request.form['food_time']
        food_type = request.form['meal-type']
        my_datetime_str = f"{food_date} {food_time}"

        data = food_type+'*'+my_datetime_str
        not_found_count=0
        for food in food_recognised:
            if food == 'food_not_found':
                not_found_count+=1
            else:
                data+='*'
                data+=food
        serving_ext = recomend.serving_ext(food_recognised)
        return render_template('market.html', items=items, chartCons=chartCon, chartReqs=chartReq, count=count, show_modal=show_modal,data=data,
                               food_recognised=food_recognised, serving_ext=serving_ext)
    
    if request.form['submitAction']=='addToDBModal':
        selected_foods = request.form.getlist('checkbox-name')
        servings = []
        flash_message_foods=""
        

        for i,food in enumerate(selected_foods):
            servings.append(int(request.form.get('servings' + food)))  
            if int(servings[i])>0:
                data=request.form.get('foods').split('*')
                mealtype = data[0]
                my_datetime_str=data[1]
                if my_datetime_str=="":
                    my_datetime = datetime.now()
                else:
                    my_datetime = datetime.strptime(my_datetime_str, '%Y-%m-%d %H:%M')
                item = Item(name=food,datetime_posted = my_datetime,mealType=mealtype, owner=current_user.id, servings=servings[i])
                db.session.add(item)
                db.session.commit()
                flash_message_foods+=food
                flash(f'You have consumed { food }, meal added to database successfully', category='success')
            else:
                flash(f'{food}, Serving size selected: {selected_foods[i]}', category='danger')



        stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
        foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
        daily_values_list=update_stats(stats_daily,foods_today_obj,'daily_values')
        
        
        # update weekely
        stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
        current_week_number = datetime.now().isocalendar()[1]
        records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
        weekly_values_list=update_stats(stats_weekly,records,'weekly_values')

        # monthly
        stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
        current_month_number = datetime.now().month
        records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
        monthly_values_list=update_stats(stats_monthly,records,'monthly_values')

        return redirect(url_for('food_page'))
    
    
    
    

    

@app.route('/items/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Food successfully deleted from your records',category='danger')

    # daily
    stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
    foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
    daily_values_list=update_stats(stats_daily,foods_today_obj,'daily_values')

    # update weekely
    stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
    current_week_number = datetime.now().isocalendar()[1]
    records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
    weekly_values_list=update_stats(stats_weekly,records,'weekly_values')

    # monthly
    stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
    current_month_number = datetime.now().month
    records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
    monthly_values_list=update_stats(stats_monthly,records,'monthly_values')
        
    return redirect(url_for('food_page'), code=301)


############### REGISTER #####################

@app.route('/register', methods=['GET','POST'])
def register_page():
    form=RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data,
                              age=form.age.data,
                              height=form.height.data,
                              weight=form.weight.data,
                              activity=form.activity.data,
                              gender=form.gender.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! Welcome to Dietian AI {user_to_create.username}', category='success')
        return redirect(url_for('food_page'))
    if form.errors != {}: #if there are no errors from the validation
        for err_msg in form.errors.values():
            flash(f'There was an error creating account: {err_msg}',category='danger')

    return render_template('register.html',form=form)



############## LOGIN #######################
@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first() 
        if attempted_user and attempted_user.check_password_correction(attemtped_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('food_page'))
        else:
            flash('Username and password do not match! Please try again', category='danger')

    return render_template('login.html', form=form)


######################## LOGOUT ##################
@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for("home_page"))




#################### ADD FOOD ####################################
UPLOAD_FOLDER = 'market/static/uploads/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


# route for addmeal
@app.route('/addmeal')
@login_required
def addmeal_page():
    count = Item.query.filter_by(owner=current_user.id).count()
    try:
        Upload.query.delete()
        db.session.commit()
        return render_template('addmeal.html',count=count)
    except:
        return render_template('addmeal.html',count=count)

# Route to upload meal image 
@app.route('/addmeal', methods=['POST','GET'])
def upload_image():
    count = Item.query.filter_by(owner=current_user.id).count()
    if request.form['submitAction']=='Add Food':
        if 'file' not in request.files:
            flash('No file part',category='danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename=='':
            flash('No image selected for uploading',category='danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

            owner =  current_user.id
            consumed_datetime = datetime.now()
            addflag=1
            upload = Upload(filename=filename, datetime_posted=consumed_datetime, owner=owner,addflag=addflag)
            db.session.add(upload)
            db.session.commit()
            # flash('Image sucessfully uploaded and displayed below', category='success')
            filenames = Upload.query.filter(Upload.addflag==1).all()
            return render_template('addmeal.html',filenames=filenames,count=count)
        
        else:
            flash('Allowed images are png, jpg, jpeg, gif only', category='danger')
            return redirect(request.url)
        

    # # Get add food to database part
    # if request.form['submitAction']=='addToDB':
    #     recent_food_object = Upload.query.filter(Upload.addflag==1).all()
    #     recent_food = recent_food_object
    #     food_recognised = recogniseFood.recogniseFood(recent_food)
    #     mealtype = request.form['meal-type']
    #     for item in food_recognised:
    #         item = Item(name=item,datetime_posted = datetime.now(),mealType=mealtype, owner=current_user.id)
    #         db.session.add(item)
    #         db.session.commit()
    #     flash(f'You have consumed {food_recognised}, meal added to database successfully', category='success')

    #     # daily
    #     stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
    #     foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
    #     daily_values_list=update_stats(stats_daily,foods_today_obj)
        
        
    #     # update weekely
    #     stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
    #     current_week_number = datetime.now().isocalendar()[1]
    #     records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
    #     weekly_values_list=update_stats(stats_weekly,records)

    #     # monthly
    #     stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
    #     current_month_number = datetime.now().month
    #     records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
    #     monthly_values_list=update_stats(stats_monthly,records)

    #     return redirect(url_for('food_page'))


  
# To display image of uploaded food
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/'+ filename), code=301)


################## Previuos MEAL ######################
# route for previous addmeal
@app.route('/previousMeals')
@login_required
def previousMeals_page():
    count = Item.query.filter_by(owner=current_user.id).count()
    try:
        Upload.query.delete()
        db.session.commit()
        return render_template('previousMeals.html',count=count)
    except:
        return render_template('previousMeals.html',count=count)



# Route to upload meal image 
@app.route('/previousMeals', methods=['POST','GET'])
def upload_image_p():
    count = Item.query.filter_by(owner=current_user.id).count()
    if request.form['submitAction']=='Add Food':
        if 'file' not in request.files:
            flash('No file part',category='danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename=='':
            flash('No image selected for uploading',category='danger')
            return redirect(request.url)
        
        if file and allowed_file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

            owner =  current_user.id
            consumed_datetime = datetime.now()
            addflag = 1;
            upload = Upload(filename=filename, datetime_posted=consumed_datetime, owner=owner, addflag=addflag)
            db.session.add(upload)
            db.session.commit()
            flash('Image sucessfully uploaded and displayed below', category='success')
            filenames = Upload.query.filter(Upload.addflag==1).all()
            return render_template('previousMeals.html',filenames=filenames,count=count)
        
        else:
            flash('Allowed images are png, jpg, jpeg, gif only', category='danger')
            return redirect(request.url)
        

    # # Get add food to database part
    # if request.form['submitAction']=='addToDB':
    #     recent_food_object = Upload.query.filter(Upload.addflag==1).all()
    #     recent_food = recent_food_object
    #     food_recognised = recogniseFood.recogniseFood(recent_food)
    #     food_date = request.form['food_date']
    #     food_time = request.form['food_time']
    #     food_type = request.form['meal-type']
    #     my_datetime_str = f"{food_date} {food_time}"
    
    #     my_datetime = datetime.strptime(my_datetime_str, '%Y-%m-%d %H:%M')
    #     for item in food_recognised:
    #         item = Item(name=item, datetime_posted = my_datetime, mealType = food_type, owner=current_user.id)
    #         db.session.add(item)
    #         db.session.commit()
    #     flash(f'You have consumed {food_recognised}, meal added to database successfully', category='success')

    #     # daily
    #     stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
    #     foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
    #     daily_values_list=update_stats(stats_daily,foods_today_obj)
        
        
    #     # update weekely
    #     stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
    #     current_week_number = datetime.now().isocalendar()[1]
    #     records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
    #     weekly_values_list=update_stats(stats_weekly,records)

    #     # monthly
    #     stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
    #     current_month_number = datetime.now().month
    #     records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
    #     monthly_values_list=update_stats(stats_monthly,records)

    #     return redirect(url_for('food_page'))


  



################ RECOMMEND NOW PAGE ######################
@app.route('/result')
@login_required
def result_page():
    count = Item.query.filter_by(owner=current_user.id).count()
    # daily
    stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
    foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
    daily_values_list=update_stats(stats_daily,foods_today_obj,'daily_values')
        
        
     # update weekely
    stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
    current_week_number = datetime.now().isocalendar()[1]
    records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
    weekly_values_list=update_stats(stats_weekly,records,'weekly_values')

    # monthly
    stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
    current_month_number = datetime.now().month
    records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
    monthly_values_list=update_stats(stats_monthly,records,'monthly_values')

    return render_template('result.html',count=count,user=current_user.username.upper(),stats_daily=stats_daily,stats_weekly=stats_weekly,stats_monthly=stats_monthly,
                           daily_values_list=json.dumps(daily_values_list),weekly_values_list=weekly_values_list, monthly_values_list=monthly_values_list)


@app.route('/result', methods=['GET', 'POST'])
def recommends_meal():
    if request.method == 'POST' and request.form.get('meal-type') != None:
        count = Item.query.filter_by(owner=current_user.id).count()
        meal_type = request.form.get('meal-type')

        # user daily calories and nutritional values
        daily_Nutritional_caloriesBased = daily_calories()
        recommend_result = recomend.recommendNow(daily_Nutritional_caloriesBased)[0:3]

        # daily
        stats_daily=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='daily_values')
        foods_today_obj = Item.query.filter(func.date(Item.datetime_posted)==date.today(), Item.owner==current_user.id).all()
        daily_values_list=update_stats(stats_daily,foods_today_obj,'daily_values')
        
        
        # update weekely
        stats_weekly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='weekly_values') 
        current_week_number = datetime.now().isocalendar()[1]
        records = Item.query.filter(db.extract('week', Item.datetime_posted) == current_week_number,Item.owner==current_user.id).all()
        weekly_values_list=update_stats(stats_weekly,records,'weekly_values')

        # monthly
        stats_monthly=Stats.query.filter(Stats.owner==current_user.id,Stats.name=='monthly_values')
        current_month_number = datetime.now().month
        records = Item.query.filter(db.extract('month', Item.datetime_posted) == current_month_number,Item.owner==current_user.id).all()
        monthly_values_list=update_stats(stats_monthly,records,'monthly_values')
        
        
        # time_now = datetime.now()
        # current_hour = int(time_now.strftime("%H"))
        # if current_hour >= 00 and current_hour <= 12:
        #     meal_type = 'Breakfast'
        # if current_hour >12 and current_hour <= 15:
        #     meal_type = 'Lunch'
        # if current_hour >15 and current_hour< 24:   
        #     meal_type='Dinner'



        return render_template('result.html',count=count, stats_daily=stats_daily,stats_weekly=stats_weekly,stats_monthly=stats_monthly,
                            user=current_user.username.upper(),recommend_result=recommend_result,daily_values_list=json.dumps(daily_values_list),
                            weekly_values_list=weekly_values_list, monthly_values_list=monthly_values_list, meal_type=meal_type)
    return redirect(url_for('result_page'))
    



########################## MEAL-LIST ##############################
@app.route('/mealList')
def mealList_page():
    if current_user.is_authenticated:
        count = Item.query.filter_by(owner=current_user.id).count()
        df = pd.read_csv("market/static/csv/food_nutrition_large.csv")
        foods = df['Name']
        return render_template('mealList.html', foods = foods,count=count)
    else:
        df = pd.read_csv("market/static/csv/food_nutrition_large.csv")
        foods = df['Name']
        return render_template('mealList.html', foods = foods)


#Calories Total_Fat Cholesterol Sodium Potassium Total_Carbohydrates Protein Calcium Iron


########################## MEAL-LIST ##############################
@app.route('/profile')
@login_required
def profile_page():
    if current_user.is_authenticated:
        count = Item.query.filter_by(owner=current_user.id).count()
        user = User.query.filter_by(id=current_user.id).first()
        activity = []
        if user.activity == '1.2':
            activity.append("Sedentary")
            activity.append("(little or no exercise)")
        if user.activity == '1.375':
            activity.append("Lightly Active")
            activity.append("(exercise 1-3 days per week)")
        if user.activity == '1.55':
            activity.append("Moderately Active")
            activity.append("(exercise 3-5 days per week)")
        if user.activity == '1.725':
            activity.append("Very Active")
            activity.append("(exercise 6-7 days per week)")
        if user.activity == '1.9':
            activity.append("Extra Active")
            activity.append("(hard exercise or physical job")

        # user daily calories and nutritional values
        daily_Nutritional_caloriesBased = daily_calories()
        return render_template('profile.html',count=count,user=user,activity=activity,daily_Nutrients=daily_Nutritional_caloriesBased)
    else:
        redirect(url_for('login_page'))


#Calories Total_Fat Cholesterol Sodium Potassium Total_Carbohydrates Protein Calcium Iron