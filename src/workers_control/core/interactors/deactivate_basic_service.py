from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


class RejectionReason(Enum):
    service_not_found = auto()
    already_deactivated = auto()


@dataclass
class Request:
    basic_service: UUID


@dataclass
class Response:
    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class DeactivateBasicServiceInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self, request: Request) -> Response:
        result = self.database_gateway.get_basic_services().with_id(
            request.basic_service
        )
        service = result.first()
        if service is None:
            return Response(rejection_reason=RejectionReason.service_not_found)
        if service.deactivated_on is not None:
            return Response(rejection_reason=RejectionReason.already_deactivated)
        result.update().set_deactivated_on(self.datetime_service.now()).perform()
        return Response(rejection_reason=None)
