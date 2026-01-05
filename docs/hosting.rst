Hosting
=======


Getting support
---------------

This application is designed to be self-hosted. If you are a community or organization that wants to host this application, 
feel free to contact IDA (`gruppe_arbeitszeit@riseup.net <mailto:gruppe_arbeitszeit@riseup.net>`_) for help.

For general information on deploying a Flask application see the
`Flask deployment documentation <https://flask.palletsprojects.com/en/stable/deploying/>`_.


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


For the app to work properly, the web server needs to be configured
with environment variables and a Python configuration file.


Environment variables
.....................


.. py:data:: WOCO_CONFIGURATION_PATH
   :no-index:
    
    (optional)

    If set, this value is used as the path to the configuration file (see below)
    instead of the default locations.


.. py:data:: ALEMBIC_CONFIG
   :no-index:

    (required)
   
    Path to the alembic configuration. Alembic is used to manage database migrations.
    This file contains settings like the location of the migration scripts or the
    database connection string. See the `alembic documentation <https://alembic.sqlalchemy.org/>`_
    for details.


Configuration file
...................


The application loads the first config file found from these locations:

* Path set in ``WOCO_CONFIGURATION_PATH`` environment variable (see above)
* ``/etc/workers-control/workers-control.py``

The configuration file must be a valid python script.
Configuration options are set as top-level variables. The following
options are available (options without defaults are required):

.. include:: config_options_GENERATED.rst
