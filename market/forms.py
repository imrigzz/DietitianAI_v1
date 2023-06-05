from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField,SelectField
from wtforms.validators import Length,EqualTo,Email,DataRequired,ValidationError
from market.models import User


class RegisterForm(FlaskForm):

    # check if user already avilable ?
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("Username already taken! Please try different username")
    
    # check if email address already avilable ?
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError("Email Address already exists! Please try different Email Address")


    username =  StringField(label='User Name', validators=[Length(min=2,max=30), DataRequired()])
    email_address = StringField(label='Email Addresss',validators=[Email(),DataRequired()])
    password1 = PasswordField(label='Password:',validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'),DataRequired()])
    gender = SelectField(label='gender', choices=[('M', 'Male'), 
                                            ('F', 'Female'), ], 
                                            validators=[DataRequired()])
    age = IntegerField(label='Age', validators=[DataRequired()])
    height = IntegerField(label='Height', validators=[DataRequired()])
    weight = IntegerField(label='Weight', validators=[DataRequired()])
    activity = SelectField(label='Weight', choices=[('1.2', 'Sedentary (little or no exercise)'), 
                                            ('1.375', 'Lightly Active (exercise 1-3 days per week)'), 
                                            ('1.55', 'Moderately Active (exercise 3-5 days per week)'), 
                                            ('1.725', 'Very Active (exercise 6-7 days per week)'), 
                                            ('1.9', 'Extra Active (hard exercise or physical job)')], 
                                            validators=[DataRequired()])
    submit = SubmitField(label='Register')


class LoginForm(FlaskForm):
    username=StringField(label='User Name', validators=[DataRequired()])
    password=PasswordField(label='Password', validators=[DataRequired()])
    submit=SubmitField(label='Sign in')


# class PurchaseItemForm(FlaskForm):
#     submit = SubmitField(label="Purchase Item!")

# class SellItemForm(FlaskForm):
#     submit = SubmitField(label="Sell Item!")
