from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.email_notifications import CompanyRegistration, EmailSender
from workers_control.core.password_hasher import PasswordHasher
from workers_control.core.repositories import DatabaseGateway


@dataclass
class RegisterCompany:
    datetime_service: DatetimeService
    email_sender: EmailSender
    password_hasher: PasswordHasher
    database: DatabaseGateway

    @dataclass
    class Response:
        class RejectionReason(Enum):
            company_already_exists = auto()
            user_password_is_invalid = auto()

        rejection_reason: Optional[RejectionReason]
        company_id: Optional[UUID]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    @dataclass
    class Request:
        email: str
        name: str
        password: str

    def register_company(self, request: Request) -> Response:
        company: Optional[records.Company]
        record = (
            self.database.get_account_credentials()
            .with_email_address(request.email)
            .joined_with_email_address_and_company()
            .first()
        )
        if not record:
            means_account = self.database.create_account()
            resources_account = self.database.create_account()
            labour_account = self.database.create_account()
            products_account = self.database.create_account()
            registered_on = self.datetime_service.now()
            self.database.create_email_address(address=request.email, confirmed_on=None)
            credentials = self.database.create_account_credentials(
                email_address=request.email,
                password_hash=self.password_hasher.calculate_password_hash(
                    request.password
                ),
            )
            self._create_confirmation_mail(request.email)
        else:
            credentials, email, company = record
            if company:
                return self.Response(
                    rejection_reason=self.Response.RejectionReason.company_already_exists,
                    company_id=None,
                )
            if not self.password_hasher.is_password_matching_hash(
                password=request.password, password_hash=credentials.password_hash
            ):
                return self.Response(
                    rejection_reason=self.Response.RejectionReason.user_password_is_invalid,
                    company_id=None,
                )
            means_account = self.database.create_account()
            resources_account = self.database.create_account()
            labour_account = self.database.create_account()
            products_account = self.database.create_account()
            registered_on = self.datetime_service.now()
        company = self.database.create_company(
            account_credentials=credentials.id,
            name=request.name,
            means_account=means_account,
            labour_account=labour_account,
            resource_account=resources_account,
            products_account=products_account,
            registered_on=registered_on,
        )
        return self.Response(rejection_reason=None, company_id=company.id)

    def _create_confirmation_mail(self, email_address: str) -> None:
        self.email_sender.send_email(CompanyRegistration(email_address=email_address))
