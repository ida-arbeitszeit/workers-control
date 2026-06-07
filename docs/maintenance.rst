Maintenance
===========


.. _updating-dependencies:

Update Dependencies
-------------------

As described earlier in this documentation, we support two different development environments:

- nix shell with nix package manager
- venv with pip package manager

We try to keep the installed packages in both environments as identical as possible. Since
nixpkgs usually provides older versions than pip, this means that we let nixpkgs handle dependency
resolution and are satisfied with the older versions from nixpkgs in both environments.
If, exceptionally, nixpkgs has a newer version, we use the older version from pip in both environments,
i.e. we have to maintain custom nix expressions for the affected packages.

This process is largely automated by the command ``python -m dev.update_dependencies``
(nix must be installed). Running it performs, in order:

#. ``nix flake update`` — refresh ``flake.lock``.
#. Refresh the custom nix pins for ``flask-babel`` and ``flask-login``
   (``dev/nix/pythonPackages/*.json``).
#. Refresh the vendored ``bulma.css``.
#. Regenerate ``constraints.txt`` (the pip-consumable pin file) from the resolved
   nix Python environment.
#. Regenerate the type stubs and auto-format the code.

Then developers using pip can upgrade by running ``pip install -r requirements-dev.txt``.

The few packages where we deliberately keep an *older* version than nixpkgs provides
(currently ``flask-login`` and ``flask-babel``) are recorded, together with the reason,
in ``VersionDowngrader.LOWER_PYPI_VERSIONS``
(``dev/update_dependencies/update_constraints.py``). Their custom nix expressions live at
``dev/nix/pythonPackages/flask-babel.nix`` and ``flask-login.nix`` (wired up in
``dev/nix/pythonPackages.nix``). These are refreshed automatically by the command above,
so you normally do not edit them by hand.


Change Dependencies
-------------------

To add or remove a *direct* dependency, edit the relevant files **without specifying
a version number** (versions are pinned afterwards by the update command). Which files
you touch depends on whether the dependency is needed at runtime or only for development.

A **runtime dependency** (needed by the app in production) is declared in three places:

- ``pyproject.toml`` → ``[project].dependencies``
- ``requirements.txt``
- ``dev/nix/pythonPackages/workers-control.nix`` → ``dependencies = [ ... ]``

A **development-only dependency** (linter, test, build or docs tool) is declared in
two places:

- ``requirements-dev.txt``
- ``dev/nix/devShell.nix`` → ``packages = [ ... ]``

Optional extras (e.g. profiling) go in ``pyproject.toml`` →
``[project.optional-dependencies]`` and in the matching ``passthru.optional-dependencies``
in ``dev/nix/pythonPackages/workers-control.nix``.

Run ``python -m dev.update_dependencies`` afterwards to pin the versions across both
environments.


Releases
--------

Maintainers regularly release new versions of the app. Procedure:

#. Increment the version number of our app in ``pyproject.toml``
   (follow https://semver.org/spec/v2.0.0.html).
#. Add a new entry to ``CHANGELOG.md`` (follow https://keepachangelog.com/en/1.1.0/).
#. Copy the constraints from ``constraints.txt`` into the dependencies in ``pyproject.toml``.
#. Create a Pull Request with label "release". This will trigger integration tests against
   the `deployment repo <https://github.com/ida-arbeitszeit/workers-control-deployment>`_.
   On failure, fix current branch or deployment repo.
#. After merging: create a new git tag (scheme: ``git tag v1.2.3 -m "Release version 1.2.3"``) and push the tag. 
   Pushing the ``vX.Y.Z`` tag triggers the ``publish-pypi.yml`` GitHub Actions workflow,
   which builds the sdist and wheel and uploads them to PyPi.


One-time PyPI release setup
...........................

Automated publishing uses `PyPI Trusted Publishing
<https://docs.pypi.org/trusted-publishers/>`_ (OIDC). Configure once by a maintainer:

#. On PyPi, open the ``workers-control`` project and add a new
   GitHub trusted publisher with: Owner ``ida-arbeitszeit``, Repository
   ``workers-control``, Workflow ``publish-pypi.yml``.
#. On Github, restrict who can create the triggering tag: add a repository ruleset
   targeting tags matching ``v*`` and a bypass list limited to maintainers/admins.


.. _translation-catalogs:

Translations
------------

We use `Flask-Babel <https://python-babel.github.io/flask-babel/>`_
for translation. The translation files reside in
:py:mod:`workers_control.flask.translations`. You find there a ``.pot`` file
as well as language-specific ``.po`` files.

Developers mark user-facing strings for translation as described in
:ref:`marking-translatable-strings`. The workflow for maintaining the
translation catalogs is as follows:

#. Add a language (optional)

   Initialize a new language::

    python -m build_support.translations initialize LOCALE
    # For example French
    python -m build_support.translations initialize fr

   Add the language to the LANGUAGES variable in :py:mod:`workers_control.flask.config.production_defaults`.

#. Update language files

   Update the ``.pot`` file with new translatable strings found
   in the source code::

    python -m build_support.translations extract

   Update language-specific ``.po`` files based on the updated
   ``.pot`` file::

    python -m build_support.translations update

#. Translate

   Translate language-specific ``.po`` files. This is the actual translation step.

   For programs that help with editing, see `this page
   <https://www.gnu.org/software/trans-coord/manual/web-trans/html_node/PO-Editors.html>`_.
   There is also an extension for the VS Code editor called "gettext".

#. Compile (optional)

   Compile ``.po`` files to ``.mo`` files. This is only necessary if you
   want to update the translations in your development
   environment. For deployment this step is automatically done by the build system::

    python -m build_support.translations compile
