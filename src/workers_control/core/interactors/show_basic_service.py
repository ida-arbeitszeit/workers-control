from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class ShowBasicServiceRequest:
    basic_service_id: UUID


@dataclass
class ShowBasicServiceResponse:
    @dataclass
    class Details:
        provider_name: str
        provider_email: str
        name: str
        description: str
        created_on: datetime

    details: Optional[Details]


@dataclass
class ShowBasicServiceInteractor:
    database_gateway: DatabaseGateway

    def show_basic_service(
        self, request: ShowBasicServiceRequest
    ) -> ShowBasicServiceResponse:
        basic_service = (
            self.database_gateway.get_basic_services()
            .with_id(request.basic_service_id)
            .first()
        )
        if basic_service is None:
            return ShowBasicServiceResponse(details=None)
        result = (
            self.database_gateway.get_members()
            .with_id(basic_service.provider)
            .joined_with_email_address()
            .first()
        )
        assert result
        member, email = result
        return ShowBasicServiceResponse(
            details=ShowBasicServiceResponse.Details(
                provider_name=member.name,
                provider_email=email.address,
                name=basic_service.name,
                description=basic_service.description,
                created_on=basic_service.created_on,
            ),
        )
