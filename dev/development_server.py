from flask import Flask

from dev.dependency_injection import (
    create_dependency_injector,
)
from dev.dev_cli import (
    create_fic_cli_group,
    create_generate_cli_group,
)

injector = create_dependency_injector()


def register_cli_commands(app: Flask) -> Flask:
    fic = create_fic_cli_group(injector)
    generate = create_generate_cli_group(injector)
    app.cli.add_command(fic)
    app.cli.add_command(generate)
    return app


def create_app() -> Flask:
    app = injector.get(Flask)
    app = register_cli_commands(app)
    return app
