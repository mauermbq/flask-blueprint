"""Routes definition for module authentication"""
from flask_babel import _
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/logout')
def logout():
    """logout user and redirect to index"""
    logout_user()
    return redirect(url_for('index'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Redirect to login form and check authentication status.
    There are actually three possible cases that need to be considered to determine
    where to redirect after a successful login:
    * If the login URL does not have a next argument, then the user is redirected to the index page.
    * If the login URL includes a next argument that is set to a relative path (or in other words,
    a URL without the domain portion), then the user is redirected to that URL.
    * If the login URL includes a next argument that is set to a full URL that includes a domain
    name, then the user is redirected to the index page. The application only redirects when the
    URL is relative in oder to ensure that the redirect stays within the same site as the
    application.

    Returns
    -------
    render_template: str
        Renders a login template from the template folder with the given context.

    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        usern = User.query.filter_by(username=form.username.data).first()
        if usern is None or not usern.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(usern, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    If User is not logged route to register form, so that users can register themselves

    validate_on_submit() conditional creates a new user with the username, email and password
    provided, writes it to the database, and then redirects to the login prompt so that the
    user can log in.

    Returns
    -------
    render_template: str
        Renders register template from the template folder with the given context.

    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        usern = User(username=form.username.data, email=form.email.data)
        usern.set_password(form.password.data)
        db.session.add(usern)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """View function for PasswordResteForm"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        userm = User.query.filter_by(email=form.email.data).first()
        if userm:
            send_password_reset_email(userm)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    When the user clicks on the email link password request view function
    is triggered
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # returns the user if the token is valid, or None
    userv = User.verify_reset_password_token(token)
    if not userv:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        userv.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
