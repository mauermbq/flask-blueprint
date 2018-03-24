"""Routes definition"""
from datetime import datetime
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from .models import User
from .forms import LoginForm, RegistrationForm, EditProfileForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Default route index
    Returns
    -------
    render_template: str
        Renders a login template from the template folder with the given context.
    """
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.before_request
def before_request():
    """
    Write the current time for a given user when user sends a request to last_seen field.
    The @before_request decorator let the decorated function to be executed before the
    view function. It's executed before any view function in the application.
    Note: when referencing current_user, Flask-Login will invoke the user loader callback
    function, which will run a database query that already put the target user in the database
    session.
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/user/<username>')  # indicate dynamic component
@login_required
def user(username):
    """
    user profile page, invoke the view function with the actual text as an argument.
    Returns
    -------
    render_template: str
        Renders a login template from the template folder with the given context.
    """
    usern = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=usern, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
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
        if usern is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """logout user and redirect to index"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
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
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Call form for user profile editing. It copys the data from the form into the user
    object and then write the object to the database. When the form is being requested
    for the first time with a GET request, the fields are prefilled with the persisted
    data. In case of a validation error nothing is written to the form fields as they
    are already populated.
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
