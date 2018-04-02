"""
Blueprint of error handler module
It's possible to defie template_folder='templates' as argument to the Blueprint() constructor.
Default is keeping html files in template subfolder.
"""
from flask import Blueprint

bp = Blueprint('errors', __name__, template_folder='templates')

from app.errors import handlers
