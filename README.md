# Flask Blueprint

## DB migration

Every time the database is modified it is necessary to generate a database migration.

```flask db migrate -m "some comment"```

then apply changes to database:

```flask db upgrade```

## SMTP debugging server

Fake email server that accepts emails, but instead of sending them, it prints them to the console.

```(venv) $ sudo python -m smtpd -n -c DebuggingServer localhost:8025```
