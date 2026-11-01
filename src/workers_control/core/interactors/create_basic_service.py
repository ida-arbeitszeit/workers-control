from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


@dataclass
class CreateBasicServiceRequest:
    member_id: UUID
    name: str
    description: str


@dataclass
class CreateBasicServiceResponse:
    class RejectionReason(Enum):
        member_not_found = auto()

    rejection_reason: Optional[RejectionReason]
    basic_service_id: Optional[UUID]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class CreateBasicServiceInteractor:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def execute(self, request: CreateBasicServiceRequest) -> CreateBasicServiceResponse:
        member = self.database_gateway.get_members().with_id(request.member_id).first()
        if member is None:
            return CreateBasicServiceResponse(
                rejection_reason=CreateBasicServiceResponse.RejectionReason.member_not_found,
                basic_service_id=None,
            )
        basic_service = self.database_gateway.create_basic_service(
            name=request.name,
            description=request.description,
            provider=member.id,
            created_on=self.datetime_service.now(),
        )
        return CreateBasicServiceResponse(
            rejection_reason=None, basic_service_id=basic_service.id
        )
