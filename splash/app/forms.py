from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField, TextAreaField, validators
from wtforms.validators import ValidationError, DataRequired, ValidationError, Length, Email, EqualTo, Regexp
from app.models import User, Community



class LoginForm(FlaskForm):
    username = StringField('User Details', validators=[DataRequired(message='Incorect Username')])
    password = PasswordField('Password', validators=[DataRequired(message='Incorrect Password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Signup(FlaskForm):
    username = StringField('Username', [validators.DataRequired(message="Username must be at least 5 characters long"), Regexp("^[A-Za-z][A-Za-z0-9_.]*$",
                0, "Usernames must be a combination of letters, numbers, dots or underscores!!!")])
    email =  EmailField('Email', [validators.Email(message='Enter a valid Email addrress!!!')])
    password = PasswordField('Password', [validators.DataRequired(message="use a strong combination!!!"), validators.Length(min=8, max=15)])
    password2 = PasswordField('Confirm Password',[validators.DataRequired(message="Re-enter password!!!"),validators.EqualTo('password', message='Mismatched Passwords!!!')])
    submit = SubmitField('Sign Up')
    
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Sorry, username already exists!!!')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Sorry, email address already in use!!!')


class EditProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Regexp("^[A-Za-z][A-Za-z0-9_.]*$",
                0, "Usernames must be a combination of letters, numbers, dots or underscores!!!")])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    #profile_pic = FileField('Profile Picture', validators=[FileRequired()])
    submit = SubmitField('submit')
    
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('username already taken!!!.')


class createChat(FlaskForm):
    username = StringField('Username', [validators.Length(min=6)])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Username does not exist')

class PasswordResetRequest(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password reset')

class ResetPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Password Reset')

class updatePassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    old_password = PasswordField('Password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Update password')

class community(FlaskForm):
    name = StringField('Name of community', validators=[DataRequired(message="You can't create a community without a name!")])
    about = TextAreaField('About community', validators=[DataRequired(message="Community must have a description!")])
    role = BooleanField('Admin' , default=False)
    submit = SubmitField('Create community')
    
    def validate_name(self, name):
        community_name = Community.query.filter_by(name=name.data).first()
        if community_name is not None:
            raise ValidationError('Sorry community already exists!')
    
class searchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')