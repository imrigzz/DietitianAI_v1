from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
from datetime import date,datetime,timezone

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address= db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    height = db.Column(db.Integer(), nullable=False)
    weight = db.Column(db.Integer(), nullable=False)
    activity = db.Column(db.String(), nullable=False)
    gender = db.Column(db.String(), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=0)
    items = db.relationship('Item', backref='owned_user', lazy=True)
    imgs = db.relationship('Upload', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    #retun if db password and login password match or not
    def check_password_correction(self, attemtped_password):
        return bcrypt.check_password_hash(self.password_hash, attemtped_password)
        
    # def can_purchase(self, item_obj):
    #     return self.budget >= item_obj.price

    # def can_sell (self,item_obj):
    #     return item_obj in self.items 

class Item(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    name= db.Column(db.String(length=30), nullable=False)
    datetime_posted= db.Column(db.DateTime, nullable=False, default=datetime.now())
    mealType= db.Column(db.String,nullable=False)
    servings = db.Column(db.Integer(),nullable=False)
    owner= db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Item{self.name}'
    
    

    # def buy(self,user):
    #     self.owner = user.id
    #     user.budget -= self.price
    #     db.session.commit()

    # def sell(self,user):
    #     self.owner=None
    #     user.budget += self.price
    #     db.session.commit()
        

class Upload(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filename= db.Column(db.String,nullable=False)
    datetime_posted= db.Column(db.DateTime, nullable=False, default=datetime.now())
    addflag = db.Column(db.Integer(), nullable=False, default=0)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

class Stats(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String,nullable=False)
    Calories= db.Column(db.Integer(), nullable=False, default=0)
    Total_Fat= db.Column(db.Integer(), nullable=False, default=0)
    Cholesterol= db.Column(db.Integer(), nullable=False, default=0)
    Sodium= db.Column(db.Integer(), nullable=False, default=0)
    Potassium= db.Column(db.Integer(), nullable=False, default=0)
    Total_Carbohydrates= db.Column(db.Integer(), nullable=False, default=0)
    Protein= db.Column(db.Integer(), nullable=False, default=0)
    Calcium= db.Column(db.Integer(), nullable=False, default=0)
    Iron= db.Column(db.Integer(), nullable=False, default=0)
    owner= db.Column(db.Integer(), db.ForeignKey('user.id'))


    def update_daily_value(self,daily_values_list):
        self.Calories=daily_values_list[0]
        self.Total_Fat=daily_values_list[1]
        self.Cholesterol=daily_values_list[2]
        self.Sodium=daily_values_list[3]
        self.Potassium=daily_values_list[4]
        self.Total_Carbohydrates=daily_values_list[5]
        self.Protein=daily_values_list[6]
        self.Calcium=daily_values_list[7]
        self.Iron=daily_values_list[8]
        db.session.commit()



