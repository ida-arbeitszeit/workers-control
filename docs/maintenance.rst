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

This process is largely automated by the command ``python -m dev.update_dependencies``.
It updates the Python packages in the nix environment and then writes the discovered version numbers
into the pip-consumable :py:mod:`constraints.txt`. To run the command, nix must be installed.

Then developers using pip can upgrade by running ``pip install -r requirements-dev.txt``.


Change Dependencies
-------------------

To add or remove a direct dependency, we do so (without specifying the version number)
in the following files:

- nix/pythonPackages/arbeitzeitapp.nix
- nix/devShell.nix
- requirements.txt
- requirements-dev.txt

Run ``python -m dev.update_dependencies`` afterwards.


Releases
--------

Maintainers publish new versions of our app on PyPi and provide an updated
NixOS module.

Procedure for a new release:

#. Increment the version number of our app in :py:mod:`pyproject.toml` and :py:mod:`nix/pythonPackages/arbeitzeitapp.nix` (follow https://semver.org/spec/v2.0.0.html)
#. Add a new entry to :py:mod:`CHANGELOG.md` (follow https://keepachangelog.com/en/1.1.0/)
#. Manually copy the exact constraints from :py:mod:`constraints.txt` into the dependencies in :py:mod:`pyproject.toml`.
#. After merging the above changes: tag the ``master`` branch (scheme: ``git tag v1.2.3 -m "Release version 1.2.3"``)
#. Create sdist and wheel via ``python -m build`` and upload to PyPi with twine: ``twine upload dist/*``
#. Update of the nixos module in the `deployment repo <https://github.com/ida-arbeitszeit/workers-control-deployment>`_
