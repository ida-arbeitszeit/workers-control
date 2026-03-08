Hosting
=======


Getting support
---------------

This application is designed to be self-hosted. If you are a community or organization that wants to host this application, 
feel free to contact IDA (`gruppe_arbeitszeit@riseup.net <mailto:gruppe_arbeitszeit@riseup.net>`_) for help.


NixOS Deployment
----------------

The IDA github organization maintains a repository with a NixOS
module for deployment on NixOS servers:
`<https://github.com/ida-arbeitszeit/workers-control-deployment>`_.


PyPi
----

The app is available on `PyPi <https://pypi.org/>`_. Try it out::
    
    pip install workers-control
    flask --app workers_control.flask.wsgi:app run


Configuration of the web server
-------------------------------

For the app to work properly, the web server needs to be configured. Three separate
applications must be able to run on the server and need configuration:

* Workers Control flask app
* Alembic (tool for database migrations)
* Email worker (a program that polls the database for pending emails and sends them out)


1. Workers Control flask app
............................

For general information on deploying a Flask application see the
`Flask deployment documentation <https://flask.palletsprojects.com/en/stable/deploying/>`_.

The flask app needs a configuration file with several options set. The path to the file
can be set by an environment variable. If the environment variable is not set, the application
expects the file in ``/etc/workers-control/workers-control.py``.

.. envvar:: WOCO_CONFIGURATION_PATH
   :no-index:
    
    (optional)

    If set, this environment variable points to the path to the configuration file.

The configuration file itself must be a valid python script. Configuration options are set as
top-level variables. The following options are available
(options without defaults are required):

.. include:: config_options_GENERATED.rst


2. Alembic
..........

Alembic is a program to manage database migrations. It needs a configuration file in a specific
format. See the `alembic documentation <https://alembic.sqlalchemy.org/>`_ for details. 

The path to the alembic configuration file is set via an environment variable:

.. ALEMBIC_SQLALCHEMY_DATABASE_URI or sqlalchemy.url in alembic.ini

.. envvar:: ALEMBIC_CONFIG
   :no-index:

    (required)
   
    Path to the alembic configuration file.


3. Email worker
...............

The email worker needs XXXXXX 
.. TODO 

.. envvar:: EMAIL_OUTBOX_DATABASE_URI
    :no-index:

    (required)

    Should be identical to flask app config option SQLALCHEMY_DATABASE_URI.

.. envvar:: MAIL_SERVER
    :no-index:

    (required)
    .. TODO


.. emailConfigurationFile = lib.mkOption {
..       type = lib.types.path;
..       description = ''
..         Path to a json file containing the mail configuration in the
..         following format:

..         {
..           "MAIL_SERVER": "mail.server.example",
..           "MAIL_PORT": "465",
..           "MAIL_USERNAME": "username@mail.server.example",
..           "MAIL_PASSWORD": "my secret mail password",
..           "MAIL_DEFAULT_SENDER": "sender.address@mail.server.example",
..           "MAIL_ADMIN": "admin.address@mail.server.example"
..         }
..       '';
..     };
