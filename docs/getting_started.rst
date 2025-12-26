Getting Started
===============


Quickstart
-----------

The following steps should get you quickly set up. You find more detailed instructions in the rest of this
document.

- The recommended development environment is Linux.
- Clone the repository from Github.
- Activate a virtual environment and run ``pip install -r requirements-dev.txt`` to install the dependencies.
- Set the following environment variables in the terminal:

.. code-block:: bash

  export FLASK_APP=arbeitszeit_development.development_server:main
  export ARBEITSZEITAPP_SERVER_NAME=127.0.0.1:5000
  export DEV_SECRET_KEY="my_secret_key"
  export ALEMBIC_CONFIG=${PWD}/arbeitszeit_development/alembic.ini
  export ARBEITSZEITAPP_TEST_DB=sqlite:///${PWD}/arbeitszeitapp_test.db
  export ARBEITSZEITAPP_DEV_DB=sqlite:///${PWD}/arbeitszeitapp_dev.db
  export ALEMBIC_SQLALCHEMY_DATABASE_URI=${ARBEITSZEITAPP_DEV_DB}

- Run ``pytest`` to run the testsuite.
- Run ``python -m build_support.translations compile`` (only if you need translations in the development app)
- Run ``flask run --debug`` to start the development app.


Database Setup
-----------------

We support both PostgreSQL and SQLite databases for testing, development and 
production. In testing and development, by default, two SQLite databases are 
created automatically in the project's root directory when starting tests or 
the development server. No manual setup is necessary.

You may use your own databases by setting the environment variables 
``ARBEITSZEITAPP_DEV_DB`` and/or ``ARBEITSZEITAPP_TEST_DB`` to point to 
databases of your choice. See :ref:`environment-variables` for details.


Virtual Environment via Nix
----------------------------

You may use `Nix <https://nixos.org>`_ as package manager and virtual environment.
While this is NOT obligatory and you may use venv and pip instead (see below),
it is indeed needed for the specific task of changing or updating
dependencies (see :ref:`updating-dependencies`).

If you are working with Nix, go to the top-level directory of the repo
and enter ``nix develop`` at the command prompt.  This will cause Nix to 
read the dependency description in ``nix.flake`` and fulfill those
dependencies in a local virtual environment. You can quit the
virtual environment by typing ``exit`` at the command prompt.

Using Nix will give you the option to access a development environment with any of the supported
python versions via ``nix develop``. Check `flake.nix` for the
supported environments under the key ``devShells``. For example to
enter a development shell with ``python3.12`` set as the default
interpreter run ``nix develop .#python312``. This will drop you into a
shell with python3.12 as the default python interpreter. This won't
change anything else on your machine and the respective python
interpreter will be garbage collected the next time you run
``nix-collect-garbage``.

When working with Nix, you may add the line ``use flake`` 
at the top of an ``.envrc`` file in the top-level directory of the repo. 
When you have Direnv installed, this will automatically invoke Nix and install 
all dependencies in the virtual environment every time you enter the root code directory. 
For the line ``use flake`` to have effect you might need to install nix-direnv. 

    **A note for Mac users:**
    By default, during Nix installation, commands are added to configure path and environment
    variables within scripts located in the global /etc directory. However, macOS updates can
    overwrite these scripts, leading to Nix becoming inaccessible. To address this issue, consider
    adding the following command to your ~/.zshrc file:

    .. code-block:: bash

      # Nix
      if [ -e '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' ]; then
        source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
      fi
      # End Nix

    see https://github.com/NixOs/nix/issues/3616 for more details.


Virtual Environment via Venv
----------------------------

If you decide to use `venv <https://docs.python.org/3/library/venv.html>`_
instead of Nix, create a virtual environment
with ``python -m venv venv``.
Then, to execute the virtual environment ``source ./venv/bin/activate``.
Within the venv environment, install all required packages: 
``pip install -r requirements-dev.txt``. You can deactivate the
virtual environment by typing ``deactivate`` at the command prompt.


.. _environment-variables:

Environment Variables
---------------------

Before you can start developing, you first have to define some
environment variables. We recommend that you define these
in an `.envrc` file in the top-level directory of the repo, and install 
`direnv <https://direnv.net/>`_ to automatically load these variables
when you enter the top-level directory of the repo.

Database URIs should be in the form
used by SQLAlchemy: ``dialect[+driver]://user:password@host:port/database[?options]``.
Commented out variables are optional. 

.. code-block:: bash

  export FLASK_APP=arbeitszeit_development.development_server:main
  export ARBEITSZEITAPP_SERVER_NAME=127.0.0.1:5000
  export DEV_SECRET_KEY="my_secret_key"
  export ALEMBIC_CONFIG=${PWD}/arbeitszeit_development/alembic.ini
  export ARBEITSZEITAPP_TEST_DB=sqlite:///${PWD}/arbeitszeitapp_test.db
  export ARBEITSZEITAPP_DEV_DB=sqlite:///${PWD}/arbeitszeitapp_dev.db
  export ALEMBIC_SQLALCHEMY_DATABASE_URI=${ARBEITSZEITAPP_DEV_DB}
  # export ALLOWED_OVERDRAW_MEMBER=1000
  # export DEFAULT_USER_TIMEZONE="Europe/Berlin"
  # export AUTO_MIGRATE=true


Development server
------------------

You can start a development app on your local machine to test your
latest changes with the command ``flask run --debug``.

Note the following features of the development app:

- There are several CLI commands to perform automated actions against
  the development database (create companies, file plans, register consumption, etc.)
  and to investigate its current state. Run
  ``flask --help`` to see the available options.

- When manually filing plans, you need
  at least one accountant to approve them. Invite
  accountants from the terminal, using the command
  ``flask invite-accountant example@mail.de``.

- Confirmation emails (e.g., for user account creation) are
  printed to ``stdout`` (your terminal). Click the confirmation
  links shown there.

- The app uses the configured development database. You can
  manually upgrade or downgrade the development database using the
  ``alembic`` command-line tool. Run ``alembic --help`` to see the
  options. If the environment variable ``AUTO_MIGRATE`` is set
  to ``true``, the database will automatically
  be upgraded when the development server starts.


Code Formatting and Analysis
-----------------------------

Run ``./format_code.py`` to format Python files automatically. 
The script uses ``black`` and
``isort``.  Currently, the script applies automatic
formatting to a limited selection of paths.  You can add more paths by
adding lines to ``.autoformattingrc``.

We use type hints.  You can check the consistency of the type hints
via the ``mypy`` command. Furthermore ``flake8`` is employed to
prevent certain mistakes, such as unused imports or
uninitialized variables. Invoke both commands without arguments to
test all the eligible code.


Testing
-------

You can run the tests by executing ``pytest`` in the root folder
of this project.

You are encouraged to use the ``./run-checks`` command before you
submit changes in a pull request.  This program runs several 
checks and the test suite.

If you have chosen to use a nix environment, the command ``nix flake check`` will test
the app against both databases, several python and nixpkgs versions. This command
is run as part of our CI Tests on Github, as well.

You can run only the tests for the part of the application 
on which you are working.  For example, if you are working on the business 
logic, you can use the following command to quickly run all the interactor 
tests:

.. code-block:: bash

  pytest tests/interactors

It is possible to disable tests that require a database to
run via an environment variable:

.. code-block:: bash

  DISABLED_TESTS="database_required" pytest

You can generate a code coverage report at ``htmlcov/index.html`` via
the command:

.. code-block:: bash

  coverage run -m pytest && coverage html


Profiling
---------

This project uses ``flask_profiler`` to provided a very basic
graphical user interface for response times. You can access this interface
at ``/profiling`` in the development server.


Documentation
-------------

To generate the developer documentation, run from the root folder of the project:

.. code-block:: bash

  make clean
  make html

Open the documentation in your
browser at ``build/html/index.html``. The HTML code is generated from
documentation files in the ``docs`` folder. 

The docs are hosted on `Read the Docs <https://workers-control.readthedocs.io/en/latest/>`_
and are automatically updated when changes are pushed to the master branch. 


Benchmarking
------------

Included in the source code for this project is a rudimentary
framework for testing the running time of our code. 
You can run all the benchmarks via
``python -m arbeitszeit_development.benchmark``.
This benchmarking tool can be
used to compare runtime characteristics across changes to the codebase. 
A contributor to the ``workers control app`` might want to compare
the results of those benchmarks from the master branch to the results
from their changes. The output of this tool is in JSON.


Using a Binary Cache for Nix
----------------------------

You can access the binary cache hosted on `cachix
<https://www.cachix.org/>`_ in your development environment if you are
using Nix to manage your development environment. The binary cache
is called "arbeitszeit".  Check the `cachix docs
<https://docs.cachix.org/getting-started#using-binaries-with-nix>`_ on
how to set this up locally.  The benefit of this for you is that you
can avoid building dependencies that are already built once in the 
continuous integration (CI) pipeline.
