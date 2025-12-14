from flask import Flask

from arbeitszeit_development.dependency_injection import create_dependency_injector
from arbeitszeit_development.dev_cli import create_generate_cli_group
from arbeitszeit_flask import create_app


def register_cli_commands(app: Flask) -> Flask:
    injector = create_dependency_injector()
    generate = create_generate_cli_group(injector)
    app.cli.add_command(generate)
    return app


def main() -> Flask:
    app = create_app()
    app = register_cli_commands(app)
    return app
