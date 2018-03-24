"""
Core container of WTForms. Forms represent a collection of fields, which can
be accessed on the form dictionary-style or attribute style. Every field has a
Widget instance. The widget’s job is rendering an HTML representation of that field.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    """Standard Login Form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """
    Registration form of the app

    The class uses stock validator for the input that comes with WTForms.
    Email validator matches the structure of an email address. Since this
    is a registration form, it is customary to ask the user to type the
    password two times to reduce the risk of a typo. When you add any methods
    that match the pattern validate_<field_name>, WTForms takes those as custom
    validators and invokes them in addition to the stock validators.
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate_username(self, username):
        """validate if user is not already in db"""
        self.user = User.query.filter_by(username=username.data).first()
        if self.user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """validate if email is not already in db"""
        self.user = User.query.filter_by(email=email.data).first()
        if self.user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    """Profile editor form"""
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        """overloaded constructor that accepts the original username as an argument"""
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """avoid duplicate username: if the user name already exists leave it untouched"""
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
