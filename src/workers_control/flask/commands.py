import subprocess

import click
from flask import current_app
from flask_babel import force_locale

from workers_control.core.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.dependency_injection import with_injection


@click.argument("email_address")
@commit_changes
@with_injection()
def invite_accountant(
    email_address: str, interactor: SendAccountantRegistrationTokenInteractor
) -> None:
    """Invite an accountant by sending a registration token to the given email address."""
    with force_locale("de"):  # type: ignore
        response = interactor.send_accountant_registration_token(
            SendAccountantRegistrationTokenInteractor.Request(email=email_address)
        )
    if response.has_been_sent:
        click.echo(
            f"An invitation has been sent to {email_address} to register as an accountant."
        )
    else:
        click.echo(
            f"An accountant with the email address {email_address} already exists. No invitation has been sent."
        )


@click.argument("args", nargs=-1)
def run_alembic(args: tuple[str, ...]) -> None:
    """Run the database migration tool alembic."""
    db_url = current_app.config["SQLALCHEMY_DATABASE_URI"]
    config = current_app.config["ALEMBIC_CONFIG"]
    subprocess.run(["alembic", "-x", f"db_url={db_url}", "-c", config, *args])
