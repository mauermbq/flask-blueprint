"""
Core container of WTForms. Forms represent a collection of fields, which can
be accessed on the form dictionary-style or attribute style. Every field has a
Widget instance. The widget’s job is rendering an HTML representation of that field.
"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class EditProfileForm(FlaskForm):
    """Profile editor form"""
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[
                             Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        """overloaded constructor that accepts the original username as an argument"""
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """avoid duplicate username: if the user name already exists leave it untouched"""
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))


class PostForm(FlaskForm):
    """Blog submission form"""
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
