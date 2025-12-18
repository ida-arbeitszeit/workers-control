Architecture
============

We employ rigorous testing when developing new features for the
application or fixing bugs.  This might seem at first like a burden to 
"rapid" development, but in our experience the opposite is the case.
The extensive test coverage allows us to work on the code without the
constant fear that it might be broken because of one of our changes.

The architecture of the program is modeled after the principles of
Clean Architecture (Robert C. Martin, *Clean Architecture*, Pearson, 2018).  Here
is a small overview of the most important
directories in the source code.

``arbeitszeit/``
    Contains the business logic of the program.  A useful heuristic for
    deciding whether your code belongs there is "Would my code still
    make sense if this app were a CLI application without a SQL
    database?"
    Use case "interactors" implement the business logic. They make use of
    the "Database Gateway" interface to persist and retrieve data. "Records"
    are business-level data structures.

``arbeitszeit_web/``
    Contains the code for implementing the Web interface.  The code in
    this directory should format and translate strings for display to
    the user and parse input data from forms and URLs.  This code is
    completly framework agnostic and is only concerned with engaging
    the business logic through the develivery mechanism of the World
    Wide Web.

``arbeitszeit_db/``
    The concrete implementation for persistence. Currently we support
    Postgres and SQLite databases via SQLAlchemy.

``arbeitszeit_flask/``
    Contains the conrete implementation for IO. We use the ``flask``
    framework.

``tests/``
   Contains all the tests.  You should find at least one test for
   every line of code in the other directories in here.

Here is a diagram that shows the main components of the application:

  .. image:: images/components_overview.svg
    :alt: Overview of the main components of workers control app
    :width: 500px
