"""This program should have no dependencies on the flask app."""

from dataclasses import dataclass
import logging
import os
import signal
import time
from datetime import UTC, datetime

from sqlalchemy import create_engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from workers_control.core.repositories import DatabaseGateway
from workers_control.db import models
from workers_control.email_sending_worker.smtp_service import (
    MailService,
    SmtpMailService,
)

logger = logging.getLogger(__name__)


def get_smtp_service() -> SmtpMailService:
    mail_server = os.environ["MAIL_SERVER"]  # where to set these?
    mail_username = os.environ["MAIL_USERNAME"]
    mail_password = os.environ["MAIL_PASSWORD"]
    mail_port = int(os.environ.get("MAIL_PORT", "587"))
    mail_encryption_type = os.environ.get("MAIL_ENCRYPTION_TYPE", "tls")

    smtp_service = SmtpMailService(
        mail_server=mail_server,
        mail_port=mail_port,
        encryption_type=mail_encryption_type,
        username=mail_username,
        password=mail_password,
    )
    return smtp_service


def get_sessionmaker() -> sessionmaker[Session]:
    db_uri_string = os.environ["SQLALCHEMY_DATABASE_URI"]  # TODO
    db_uri = make_url(db_uri_string)
    engine = create_engine(db_uri)
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return SessionLocal


RUNNING = True
POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 5


def shutdown(signum, frame):
    global RUNNING
    RUNNING = False


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)


# how to make it testable? dependency injection?
# - pass fake mail_service
# - pass fake db 
# - pass fake datetime_service
@dataclass
class EmailWorker:
    mail_service: MailService
    database_gateway: DatabaseGateway

    def run(self) -> None:
        logger.info("Email worker started")

        while RUNNING:
            with sessionmaker_() as session:
                emails = (  # use database_gateway instead
                    session.query(models.EmailOutbox)
                    .filter(models.EmailOutbox.sent_at.is_(None))
                    .order_by(models.EmailOutbox.created_at)
                    .limit(BATCH_SIZE)
                    .all()
                )

                if not emails:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                for email in emails:
                    try:
                        self.mail_service.send_message(
                            subject=email.subject,
                            recipient=email.recipient,
                            html=email.html,
                            sender=email.sender,
                        )
                        email.sent_at = datetime.now(UTC)  # UTC correct?
                    except Exception as exc:
                        email.retry_count += 1  # we do not use retry_count!?
                        email.last_error = str(exc)

                session.commit()

        logger.info("Email worker stopped")


if __name__ == "__main__":
    smtp_service = get_smtp_service()
    
    email_worker = EmailWorker(smtp_service, database_gateway)
    email_worker.run()
