# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-12-30

### Changed

- Rename nix package name from "arbeitszeitapp" to "workers-control" (#1364)
- Rename occurrences of "Arbeitszeitapp" to "Workers Control app" in user facing strings and update translations (#1367)
- Rename source code variables and deployment options to "workers control" (#1366)
- Change source code folder structure from "flat" to "src" layout (#1362)
- Change default config file location to "/etc/workers-control/workers-control.py" (#1366)
- Rename folder "arbeitszeit_development" to "dev" (#1362)
- Update instructions for developers and downstream users in our developer's documentation, especially regarding changed environment variables.

### Removed

- Our rudimentary web API (#1359)

### Fixed

- Bug in code formatter that prevented formatting nix files (#1365)
- Added missing package "build" to dev dependencies for programmers using pip/venv (#1363)

## [0.1.1] - 2025-12-26

### Fixed

- Add build support files to MANIFEST.in (#1360)

## [0.1.0] - 2025-12-25

### Added

- Start versioning and using a changelog (#1358)
