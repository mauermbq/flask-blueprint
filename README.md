# Flask Blueprint

First of all honor to [Miguel Grinberg](https://blog.miguelgrinberg.com/index) and his amazing
[blog series on his  "Flask Mega tutorial"](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).
I reused his example (including some hints from his blog) for a private mini project since it is a really good starting point from where you can build your own web apps.

**My motivation:**

I learned python in context of some ML and deep learning activities, but I'm intending to have a baseline for an productive app.

**My two cents:**

I'm starting to add some further generalizations and put it into an IaaS independent docker composite:

* integrate with redis also including ML model injection
* put it behind a proxy - for instance [nginx](https://github.com/kubernetes/ingress-nginx) and [treafik](https://github.com/containous/traefik/blob/master/docs/user-guide/kubernetes.md) are good candidates to use it as an ingess controller for kubernetes

## How to use it

### Flask application context

The application context never moves between threads and it will not be shared between requests. As such it is the right place to store database connection information and other things. Starting with Flask 0.10 flask [g.object](http://flask.pocoo.org/docs/0.12/api/#flask.g) is stored on the application context.

create_app() constructs a Flask application instance, and eliminate the global variable. Extension instances are first created in the global scope  which are not attached to the application. At the time the application instance is created in the factory function, the init_app() method must be invoked on the extension instances to bind it to the now known application.

This is especially helpful when using the Flask Blueprint mechanisma (see [Creating a reusable package](http://flask-appfactory.readthedocs.io/en/latest/tut_package.html).

### Documentation

Unlike block comments, docstrings are built into the Python language itself. This means you can utlize Python’s introspection capabilities to access docstrings at runtime, calso. Docstrings are accessible from both the ```__doc__```, as well as with the built in help() function.

More about docsring and his magic: [see "The Htchhiker's Guide to python":](http://docs.python-guide.org/en/latest/writing/documentation/#docstring-ref)

### DB migration

Every time the database is modified it is necessary to generate a database migration by Migration tool.
For this Flask-Migrate extension needs to be installed.

```flask db migrate -m "some comment"```

then apply changes to database:

```flask db upgrade```

### Translations

Install [Flask-Babel](https://pythonhosted.org/Flask-Babel/): `(venv) $ pip install flask-babel`

Once all the wrapper functions _() and _l() are in place, use the pybabel command to extract them to a .pot file, which stands for portable object template.

babel.cfg is required for this.

Extract .pot file: `(venv) $ pybabel extract -F babel.cfg -k _l -o messages.pot .`

Generate lanuage catalog: `(venv) $ pybabel init -i messages.pot -d app/translations -l de`

The command will create a es subdirectory inside this directory for the German data files. In particular, there will be a new file named app/translations/de/LC_MESSAGES/messages.po, that is where the translations need to be made.

Compile for translation: `(venv) $ pybabel compile -d app/translations`

This command adds a messages.mo file next to messages.po in each language repository.

Updates:

```bash
(venv) $ pybabel extract -F babel.cfg -k _l -o messages.pot .
(venv) $ pybabel update -i messages.pot -d app/translations
```

## Flask Mail

Fake email server for local development that accepts emails, but instead of sending them, it prints them to the console.

```bash
(venv) $ sudo python -m smtpd -n -c DebuggingServer localhost:8025
(venv) $ export MAIL_SERVER=localhost
(venv) $ export MAIL_PORT=8025
```

Via Mail server:

```bash
(venv) $ export MAIL_SERVER=<mailserver>
(venv) $ export MAIL_PORT=587
(venv) $ export MAIL_USE_TLS=1
(venv) $ export MAIL_USERNAME=<your-mail-username>
(venv) $ export MAIL_PASSWORD=<your-mail-password>
```

Using Flask Mail:

```python
>>> from flask_mail import Message
>>> from app import mail
>>> msg = Message('your subject', sender=app.config['ADMINS'][0],
... recipients=['your-email@example.com'])
>>> msg.body = 'your mail body'
>>> msg.html = '<h1>your HTML body</h1>'
>>> mail.send(msg)
```

## Registration

There is a discussion why not using `flask-user` module?
Imho using it or not using it is a trade-off discussion like why do you write your own microblog app.

## Save your extra packages

 `pip freeze > requirements.txt`