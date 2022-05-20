from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField, TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,Length,ValidationError
from pitch_me.models import User


class RegForm(FlaskForm):
    username = StringField('Enter Your Username', validators=[DataRequired(), Length(min=4,max=25)])
    email = StringField('Your Email Address', validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    password_confirm = PasswordField('Confirm Passwords',validators = [DataRequired(), EqualTo('password',message = 'Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()        
        if user:
            raise ValidationError('that username is already taken. Please choose another username')
        
        
    def validate_email(self, email):
        
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The email address is already taken. Please choose another email address")


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me!')
    submit = SubmitField('Login')
    
class UpdateAccountForm(FlaskForm):
    username = StringField('Enter Your Username', validators=[DataRequired(), Length(min=4,max=25)])
    email = StringField('Your Email Address', validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png']),])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:   
            user = User.query.filter_by(username=username.data).first()        
            if user:
                raise ValidationError('that username is already taken. Please choose another username')
        
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("The email address is already taken. Please choose another email address")

class PitchForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Pitch')
    
