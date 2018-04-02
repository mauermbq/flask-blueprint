"""
Shortcut commands for managing language translations.

Flask relies on [Click](http://click.pocoo.org/5/) for command-line operations.
The name of the command comes from the name of the decorated function, and the
help message comes from the docstring. The docstrings for these functions are
used as help message in the --help output.
Note:
current_app variable does not work in this case because these commands are registered
at start up, not during the handling of a request. Use register() function that takes
the app instance as an argument.
Usage:
(venv) $ flask translate init <language-code>
(venv) $ flask translate update
(venv) $ flask translate compile
"""
import os
import click


def register(app):
    """register app module"""
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')
