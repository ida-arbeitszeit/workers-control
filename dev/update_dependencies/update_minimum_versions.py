#!/usr/bin/env python
from __future__ import annotations

import argparse
import logging
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import Version

from ..command import Shell, SubprocessRunner
from .update_constraints import (
    PythonEnvironment,
    PythonPackage,
    VersionDowngrader,
    VersionStringCleaner,
)

logger = logging.getLogger(name=__name__)


def main(subprocess_runner: SubprocessRunner) -> None:
    updater = MinimumVersionsUpdater(
        pyproject_file=PyprojectFile(path=Path("pyproject.toml")),
        python_environment=PythonEnvironment(subprocess_runner),
        version_string_cleaner=VersionStringCleaner(),
        version_downgrader=VersionDowngrader(),
    )
    updater.update_minimum_versions()


@dataclass
class MinimumVersionsUpdater:
    pyproject_file: PyprojectFile
    python_environment: PythonEnvironment
    version_string_cleaner: VersionStringCleaner
    version_downgrader: VersionDowngrader

    def update_minimum_versions(self) -> None:
        installed_packages = {
            canonicalize_name(package.name): package
            for package in self.python_environment.get_installed_packages()
        }
        dependencies = self.pyproject_file.read_dependencies()
        for dependency in dependencies:
            installed_package = installed_packages.get(
                canonicalize_name(dependency.name)
            )
            if installed_package is None:
                raise RuntimeError(
                    f"Runtime dependency {dependency.name} is not installed in the python environment."
                )
            minimum_version = self.version_string_cleaner.clean_version_string(
                self._get_lowest_tested_version(installed_package)
            )
            logger.info(
                "Set minimum version of %s to %s", dependency.name, minimum_version
            )
            dependency.specifier = SpecifierSet(f">={minimum_version}")
        self.pyproject_file.write_dependencies(dependencies)

    def _get_lowest_tested_version(self, package: PythonPackage) -> str:
        if not self.version_downgrader.pypi_version_number_is_lower_than_nixpkgs(
            package.name
        ):
            return package.version
        pypi_version = self.version_downgrader.downgrade_to_pypi(package.name)
        return min(package.version, pypi_version, key=Version)


@dataclass
class PyprojectFile:
    path: Path

    DEPENDENCIES_ARRAY = re.compile(
        r"^dependencies = \[$.*?^\]$", flags=re.MULTILINE | re.DOTALL
    )

    def read_dependencies(self) -> list[Requirement]:
        with open(self.path, "rb") as handle:
            pyproject = tomllib.load(handle)
        return [
            Requirement(dependency)
            for dependency in pyproject["project"]["dependencies"]
        ]

    def write_dependencies(self, dependencies: list[Requirement]) -> None:
        array = (
            "dependencies = [\n"
            + "".join(f'    "{dependency}",\n' for dependency in dependencies)
            + "]"
        )
        content, replacements = self.DEPENDENCIES_ARRAY.subn(
            lambda _: array, self.path.read_text()
        )
        assert replacements == 1
        self.path.write_text(content)


def parse_arguments() -> None:
    parser = argparse.ArgumentParser(
        description="Set the minimum versions of the runtime dependencies in pyproject.toml to the versions installed in the current python environment.  This command must be run in the nixos-stable development shell."
    )
    parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parse_arguments()
    main(Shell())
