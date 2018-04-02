"""Routes definition"""
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post
from app.translate import translate
from app.main import bp


@bp.before_app_request
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
    # add the locale to the g object so that it accessible from base template
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Default route index.
    The paginate method can be called on any query object from Flask-SQLAlchemy.
    Objects in order to create pagination links:
    has_next: True if there is at least one more page after the current one
    has_prev: True if there is at least one more page before the current one
    next_num: page number for the next page
    prev_num: page number for the previous page
    Returns
    -------
    render_template: str
        Renders index from the template folder with the given context.
    """
    form = PostForm()
    if form.validate_on_submit():
        # try to detect language
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data,
                    author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    # Pagination object: items contains the list of items in the requested page.
    # Page 1, explicit: http://localhost:5000/index?page=1
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
    """
    Same as index, but show a global post stream from all users
    and does not have form obeject to write blog posts
    """
    page = request.args.get('page', 1, type=int)
    # pagination object (see above)
    posts = Post.query.order_by(
        Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template("index.html", title=_('Explore'), posts=posts.items)

@bp.route('/user/<username>')  # indicate dynamic component
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
    page = request.args.get('page', 1, type=int)
    posts = usern.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=usern.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=usern.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=usern, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    """route to follow a user"""
    user_follow = User.query.filter_by(username=username).first()
    if user_follow is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user_follow == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user_follow)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """route to unfollow a user"""
    user_unfollow = User.query.filter_by(username=username).first()
    if user_unfollow is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user_unfollow == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user_unfollow)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """call translate function that wraps cloud service of your choice"""
    translation = translate(request.form['text'],
                            request.form['source_language'],
                            request.form['dest_language'])
    return jsonify({'text': translation})
