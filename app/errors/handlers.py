"""Error handler for flask (works similar to view functions)"""
from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    """HTTP 404 not found error"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """The error handler for http 500 errors should be invoked after a database errors"""
    # rollback in order to avoid inference of db sessions with template access
    db.session.rollback()
    return render_template('500.html'), 500
