"""
Blueprint of authentication module
It's possible to defie template_folder='templates' as argument to the Blueprint() constructor.
Default is keeping html files in template subfolder.
"""
from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates')

# avoid circular dependencies
# pylint: disable=C0413
from app.auth import routes
