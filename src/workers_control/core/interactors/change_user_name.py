from __future__ import annotations

import enum
from dataclasses import dataclass
from uuid import UUID

from workers_control.core.email_notifications import (
    EmailSender,
    NameChangeConfirmation,
)
from workers_control.core.password_hasher import PasswordHasher
from workers_control.core.repositories import DatabaseGateway

MAX_NAME_LENGTH = 150


@dataclass
class Request:
    user_id: UUID
    new_name: str
    current_password: str


@dataclass
class Response:
    class RejectionReason(Exception, enum.Enum):
        invalid_name = enum.auto()
        user_not_found = enum.auto()
        incorrect_password = enum.auto()

    rejection_reason: RejectionReason | None


@dataclass
class ChangeUserNameInteractor:
    database: DatabaseGateway
    email_sender: EmailSender
    password_hasher: PasswordHasher

    def change_user_name(self, request: Request) -> Response:
        if not request.new_name or len(request.new_name) > MAX_NAME_LENGTH:
            return Response(rejection_reason=Response.RejectionReason.invalid_name)

        member_query = self.database.get_members().with_id(request.user_id)
        company_query = self.database.get_companies().with_id(request.user_id)
        accountant_query = self.database.get_accountants().with_id(request.user_id)
        matching_query = member_query or company_query or accountant_query

        record = matching_query.joined_with_email_address().first()
        if not record:
            return Response(rejection_reason=Response.RejectionReason.user_not_found)

        _, email = record
        credentials = (
            self.database.get_account_credentials()
            .with_email_address(email.address)
            .first()
        )
        if not credentials or not self.password_hasher.is_password_matching_hash(
            request.current_password, credentials.password_hash
        ):
            return Response(
                rejection_reason=Response.RejectionReason.incorrect_password
            )

        matching_query.update().set_name(request.new_name).perform()
        self.email_sender.send_email(
            NameChangeConfirmation(
                email_address=email.address,
                new_name=request.new_name,
            )
        )
        return Response(rejection_reason=None)
