"""
Module for sending emails.
See config.py for required env variables for deployment
see https://pythonhosted.org/Flask-Mail/
Note: current_app is a context-aware variable that is tied to the thread that is
handling the client request. So i a different Thread this object would not have
a value assigned. That's why we access real application instance by 
current_app._get_current_object()
"""
from threading import Thread
from flask_mail import Message
from flask import current_app
from app import mail

def send_async_email(app, msg):
    """
    Sending an email slows the application down considerably so we use background thread.
    Python has support for running asynchronous tasks in more than one way (threading and
    multiprocessing modules). Starting a background thread for email is much less resource
    intensive than starting a new process
    """
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """simple mail helper function for sending out mails withou CC and BCC"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # start async thread for sending email
    # pylint: disable=W0212
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
