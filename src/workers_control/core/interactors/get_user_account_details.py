from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, Union
from uuid import UUID

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class GetUserAccountDetailsInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def get_user_account_details(self, request: Request) -> Response:
        record: Optional[
            Tuple[
                Union[records.Member, records.Company, records.Accountant],
                records.EmailAddress,
            ],
        ] = (
            (
                self.database.get_members().with_id(request.user_id)
                or self.database.get_companies().with_id(request.user_id)
                or self.database.get_accountants().with_id(request.user_id)
            )
            .joined_with_email_address()
            .first()
        )
        if not record:
            return self._create_failure_model()
        else:
            user, mail = record
            user_name = user.get_name()
            return self._create_success_model(user.id, mail, user_name)

    def _create_success_model(
        self, user_id: UUID, email_address: records.EmailAddress, user_name: str
    ) -> Response:
        return Response(
            user_info=UserInfo(
                id=user_id,
                name=user_name,
                email_address=email_address.address,
                current_time=self.datetime_service.now(),
                email_address_confirmation_timestamp=email_address.confirmed_on,
            )
        )

    def _create_failure_model(self) -> Response:
        return Response(user_info=None)


@dataclass
class Request:
    user_id: UUID


@dataclass
class Response:
    user_info: Optional[UserInfo]


@dataclass
class UserInfo:
    id: UUID
    name: str
    email_address: str
    current_time: datetime
    email_address_confirmation_timestamp: Optional[datetime] = None
