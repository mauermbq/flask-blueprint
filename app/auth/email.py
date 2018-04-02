"""
Module for sending emails for auth handling.
See config.py for required env variables for deployment
see https://pythonhosted.org/Flask-Mail/
"""
from flask_babel import _
from app.email import send_email
from flask import render_template, current_app

def send_password_reset_email(user):
    """generate the password reset emails"""
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
