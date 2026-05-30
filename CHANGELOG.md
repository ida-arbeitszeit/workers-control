# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The nix package now reads its version from `pyproject.toml`, so the release version only needs to be bumped in one place.

## [0.2.2] - 2026-05-30

### Changed

- Automate publishing to PyPI. (#1496)

### Fixed

- Fix a foreign key violation that could occur when changing a user's email address. (#1495)

## [0.2.1] - 2026-05-26

### Added

- Functionality for members, companies and accountants to change their name. (#1492)
- The provider's email address is now shown in the basic service detail view. (#1481)

### Changed

- Emails are now sent through a transactional outbox, so they are only dispatched after the database transaction has committed. (#1484, #1485, #1486, #1487)
- Refactor member and company request handlers into separate view classes. (#1488, #1489)
- Improve documentation for the `SECRET_KEY` and `SECURITY_PASSWORD_SALT` settings. (#1490)
- Verify documentation generation as part of the `run-checks` script. (#1491)
- Update dependencies.
- Update translations.

## [0.2.0] - 2026-05-06

### Added

- Private consumption of basic services for members. (#1446, #1449)
- Productive consumption of basic services for companies, including a consumption details view. (#1453, #1456, #1457, #1459, #1461)
- New transfer types for private and productive consumption of basic services. (#1431)
- Listing of consumed basic services in the member consumption list, with a new consumption details view. (#1451)
- Consumption link on the "all plans" list, allowing members and companies to consume products directly from there. A colored tag signals to companies that a plan is their own. (#1434)
- Plan preview on the member private consumption form, mirroring the existing company flow. (#1433)
- Deduction of the contribution to public plans on basic-service consumption. (#1466)
- Inclusion of consumed basic services in the payout factor (FIC) calculation. (#1468)
- Basic service consumptions are now shown in the FIC details view. (#1470)
- Functionality for workers to deactivate their basic service offers. (#1473, #1474)
- Counter for basic services on the global statistics page. (#1478)
- User name in the user account info. (#1460)

### Changed

- Unify "query plans" and "query basic services" into a single "Search offers" workflow accessible from member and company dashboards. (#1443, #1444)
- Move the "create new plan" button from the company dashboard to the "My plans" view. (#1438)
- Move the "register hours worked" button from the company dashboard to the "registered hours worked" view, and improve related redirections and navigation bar. (#1439)
- Improve developer documentation on core concepts. (#1476)
- Update translations. (#1448, #1475)

### Removed

- "Latest plans" panel from member and company dashboards. (#1435)
- "Latest plans" section from the start page. (#1464)
- "Private consumption" button from the member dashboard; the main entry point is now the "all plans" list. (#1436)
- "Productive consumption" button from the company dashboard; the main entry point is now the "all plans" list. (#1437)
- Duplicated information from member and company dashboards. (#1460)

### Fixed

- Nix flake checks could hang on failure when PostgreSQL was not terminated; a trap now kills it on exit. (#1430)

## [0.1.7] - 2026-04-24

### Added

- "Create basic service" functionality. (#1423)
- "Show basic service" functionality. (#1414)
- "List worker's basic services" functionality. (#1421)
- "Query basic services" functionality. (#1427)

### Removed

- Unclear graph and metrics from statistics page. (#1418)

### Fixed

- Don't force HTTPS on http dev server. (#1420)

## [0.1.6] - 2026-03-22

### Added

- Password reset functionality for members, companies and accountants. Users can request a password reset via a "Forgot password?" button on the login pages. (#1404)
- User timezone detection from the browser. Timestamps are now displayed in the user's local timezone instead of the server's timezone. (#1402)
- Documentation for inviting accountants via CLI in production. (#1398)

### Changed

- Rework accountant registration use case. Improve user feedback on invite-accountant CLI command. Display warning to users when a registration token is invalid. (#1401)
- Use SQLAlchemy's native Uuid type for UUID columns, eliminating manual UUID/string conversions in the repository layer. Includes a database migration. (#1403)
- Add bash to nix devShell as a workaround for a GitHub Copilot CLI bug. (#1400)
- Update German and Spanish translations. (#1407)

### Removed

- Back button from the start page. (#1399)

## [0.1.5] - 2026-03-10

### Added

- Web route showing details around the payout factor (FIC). Users can access the page via a link on the "Statistics" page. (#1380)
- Date and message ID headers for emails. (#1384)

### Fixed

- SQLite test database path to use temporary directory, which allows parallel test runs in the nix development environment. (#1385)
- F-strings did not get translated. They have been replaced by % substitution strings. (#1387)
- Timestamps on the x-axes of several line plots have been shown in a confusing format. Formatting has been improved. (#1378)

### Changed

- Instead of using the 3rd party package Flask-Mail, we now use our own SMTP module for submitting mails. Remove production config options MAIL_PLUGIN_MODULE, MAIL_PLUGIN_CLASS, MAIL_USE_TLS and MAIL_USE_SSL. Add new option MAIL_ENCRYPTION_TYPE which can take the values "ssl or "tls". Hosting docs have been adapted. (#1386)
- Developers run database migration via "flask db" instead of the "alembic"
command directly. In development, environment variables ALEMBIC_CONFIG and ALEMBIC_SQLALCHEMY_DATABASE_URI are not needed anymore. In production,
the formerly obligatory environment variable ALEMBIC_CONFIG is now an optional configuration option, and a default alembic configuration file for production has been added. (#1396)

## [0.1.4] - 2026-01-05

### Fixed

- Added missing logging configuration file to source distribution.

## [0.1.3] - 2026-01-05

### Added

- Public Sector Fund (PSF) transfers view. Users can access the new view via the "global statistics" page (#1374)

### Changed

- Rework logging, define loggers instead of relying primarily on root logger (#1371)
- Update dependencies and translations (#1375)

### Fixed

- Bug in Public Sector Fund (PSF) balance calculation, which has been lead to incorrect calculation of the PSF balance (#1372)

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
