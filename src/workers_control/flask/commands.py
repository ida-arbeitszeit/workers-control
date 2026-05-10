import subprocess

import click
from flask import current_app
from flask_babel import force_locale

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.injector import Injector
from workers_control.core.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)
from workers_control.core.repositories import DatabaseGateway
from workers_control.db import commit_changes
from workers_control.db.db import Database
from workers_control.email_sending_worker.worker import EmailWorker
from workers_control.flask.dependency_injection import with_injection
from workers_control.flask.mail_sender import provide_email_sender


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


@with_injection()
def send_emails(
    database_gateway: DatabaseGateway,
    datetime_service: DatetimeService,
    injector: Injector,
) -> None:
    """Drain the email outbox via the configured ``MAIL_SENDER_PLUGIN``.

    Run this as a separate long-running process (e.g. under systemd). It uses
    the same Flask configuration file as the web app.
    """
    mail_service = provide_email_sender(injector)
    db = Database()
    worker = EmailWorker(
        mail_service=mail_service,
        database_gateway=database_gateway,
        datetime_service=datetime_service,
        commit=db.session.commit,
    )
    worker.run()
