Maintenance
===========


.. _updating-dependencies:

Update Dependencies
-------------------

Nixpkgs resolves the dependencies for both development environments, the nix shell
and the pip venv. Run ``python -m dev.update_dependencies`` (requires nix). It

#. updates ``flake.lock`` and the vendored ``bulma.css``,
#. writes the versions of the nixos-unstable shell to ``constraints.txt``,
#. sets the minimum versions in ``pyproject.toml`` to the versions of the nixos-stable shell,
#. regenerates the type stubs and formats the code.

Developers using pip then run ``pip install -r requirements-dev.txt``.

``pyproject.toml`` has no upper bounds, so that new releases of a dependency don't require
a new release of the app. The tested range reaches from the nixos-stable versions
(``*-nixpkgs-stable`` flake checks) to the versions in ``constraints.txt``.

If pip can't install a version from nixpkgs (e.g. it isn't on PyPI yet), add the package with
its PyPI version and the reason to ``VersionDowngrader.LOWER_PYPI_VERSIONS``
(``dev/update_dependencies/update_constraints.py``).


Change Dependencies
-------------------

Add or remove a direct dependency without a version number, then run
``python -m dev.update_dependencies``:

- **Runtime** (needed to run the app, including every package imported in ``src/``):
  ``[project].dependencies`` in ``pyproject.toml`` and ``dependencies`` in
  ``dev/nix/pythonPackages/workers-control.nix``.
- **Development only** (everything else, e.g. linters, test, build and docs tools):
  ``requirements-dev.txt`` and ``packages`` in ``dev/nix/devShell.nix``.


Releases
--------

Maintainers regularly release new versions of the app. Procedure:

#. Increment the version number of our app in ``pyproject.toml``
   (follow https://semver.org/spec/v2.0.0.html).
#. Add a new entry to ``CHANGELOG.md`` (follow https://keepachangelog.com/en/1.1.0/).
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

We use gettext message catalogs for translation. The app loads them with
Python's :py:mod:`gettext` module, and `Babel <https://babel.pocoo.org/>`_
maintains and compiles them. The translation files reside in
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
