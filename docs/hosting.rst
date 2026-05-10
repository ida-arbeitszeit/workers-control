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


Configuration file
...................


The application loads the first config file found from these locations:

* Path set in ``WOCO_CONFIGURATION_PATH`` environment variable (see above)
* ``/etc/workers-control/workers-control.py``

The configuration file must be a valid python script.
Configuration options are set as top-level variables. The following
options are available (options without defaults are required):

.. include:: config_options_GENERATED.rst


Inviting accountants
--------------------

To invite an accountant, use the ``invite-accountant`` CLI command
with the accountant's email address::

    flask --app workers_control.flask.wsgi:app invite-accountant example@mail.de

This sends an email with a registration link to the given address.


Email sending worker
--------------------

Outbound email is delivered asynchronously by a separate worker process.
The Flask app writes outbound messages to an ``email_outbox`` database
table inside the same transaction as the data change that triggered them
(transactional outbox pattern). A long-running worker polls that table,
sends each message via SMTP, and records success or failure on the row.

Run the worker with::

    flask --app workers_control.flask.wsgi:app send-emails

The worker should be supervised so that it is restarted automatically. A
minimal systemd service unit looks like this::

    [Unit]
    Description=Workers Control email sending worker
    After=network.target

    [Service]
    Type=simple
    Environment=WOCO_CONFIGURATION_PATH=/etc/workers-control/workers-control.py
    ExecStart=/usr/bin/flask --app workers_control.flask.wsgi:app send-emails
    Restart=on-failure
    RestartSec=5s

    [Install]
    WantedBy=multi-user.target

Without a running worker, mail accumulates in the ``email_outbox`` table
but is never delivered.

The worker's delivery backend is selected via the ``MAIL_SENDER_PLUGIN``
configuration option. The default,
``workers_control.email_sending_worker.smtp_service:SmtpMailService``,
delivers via SMTP using the standard ``MAIL_SERVER``, ``MAIL_PORT``,
``MAIL_ENCRYPTION_TYPE``, ``MAIL_USERNAME`` and ``MAIL_PASSWORD`` settings.
You normally do not need to change this; it exists so that development and
test environments can substitute a non-SMTP backend that simply logs each
message.
