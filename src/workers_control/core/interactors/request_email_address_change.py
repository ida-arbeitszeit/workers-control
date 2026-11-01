from __future__ import annotations

import enum
from dataclasses import dataclass

from workers_control.core.email import is_possibly_an_email_address
from workers_control.core.email_notifications import (
    EmailChangeConfirmation,
    EmailChangeWarning,
    EmailSender,
)
from workers_control.core.password_hasher import PasswordHasher
from workers_control.core.repositories import DatabaseGateway


@dataclass
class RequestEmailAddressChangeInteractor:
    database: DatabaseGateway
    email_sender: EmailSender
    password_hasher: PasswordHasher

    def request_email_address_change(self, request: Request) -> Response:
        if reason := self._validate_request(request):
            return Response(rejection_reason=reason)
        self.email_sender.send_email(
            EmailChangeWarning(old_email_address=request.current_email_address)
        )
        self.email_sender.send_email(
            EmailChangeConfirmation(
                old_email_address=request.current_email_address,
                new_email_address=request.new_email_address,
            )
        )
        return Response(rejection_reason=None)

    def _validate_request(self, request: Request) -> Response.RejectionReason | None:
        if not is_possibly_an_email_address(request.new_email_address):
            return Response.RejectionReason.invalid_email_address
        elif not bool(
            self.database.get_email_addresses().with_address(
                request.current_email_address
            )
        ):
            return Response.RejectionReason.current_email_address_does_not_exist
        elif bool(
            self.database.get_email_addresses().with_address(request.new_email_address)
        ):
            return Response.RejectionReason.new_email_address_already_taken
        elif not self._is_password_matching(request):
            return Response.RejectionReason.incorrect_password
        return None

    def _is_password_matching(self, request: Request) -> bool:
        credentials = (
            self.database.get_account_credentials()
            .with_email_address(request.current_email_address)
            .first()
        )
        if not credentials:
            return False
        return self.password_hasher.is_password_matching_hash(
            request.current_password, credentials.password_hash
        )


@dataclass
class Request:
    current_email_address: str
    new_email_address: str
    current_password: str


@dataclass
class Response:
    class RejectionReason(enum.Enum):
        invalid_email_address = enum.auto()
        current_email_address_does_not_exist = enum.auto()
        new_email_address_already_taken = enum.auto()
        incorrect_password = enum.auto()

    rejection_reason: RejectionReason | None
