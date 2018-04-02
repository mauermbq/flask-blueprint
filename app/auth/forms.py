"""
Core container of WTForms. Forms represent a collection of fields, which can
be accessed on the form dictionary-style or attribute style. Every field has a
Widget instance. The widget’s job is rendering an HTML representation of that field.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    """Standard Login Form"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


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
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate_username(self, username):
        """validate if user is not already in db"""
        self.user = User.query.filter_by(username=username.data).first()
        if self.user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        """validate if email is not already in db"""
        self.user = User.query.filter_by(email=email.data).first()
        if self.user is not None:
            raise ValidationError(_('Please use a different email address.'))

class ResetPasswordRequestForm(FlaskForm):
    """Password reset form via Email"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    """Request the user to reset password """
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
