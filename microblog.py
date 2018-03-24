"""Microblog dem app"""
from app import app, db
from app.models import User, Post

app.run(debug=True)

@app.shell_context_processor
def make_shell_context():
    """shell context"""
    return {'db': db, 'User': User, 'Post': Post}
