from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class ListedBasicService:
    id: UUID
    name: str
    description: str
    created_on: datetime


@dataclass
class Response:
    basic_services: list[ListedBasicService]


@dataclass
class Request:
    member: UUID


@dataclass
class ListBasicServicesOfWorkerInteractor:
    database_gateway: DatabaseGateway

    def list_basic_services_of_worker(self, request: Request) -> Response:
        records = (
            self.database_gateway.get_basic_services()
            .of_provider(request.member)
            .that_are_active()
        )
        return Response(
            basic_services=[
                ListedBasicService(
                    id=record.id,
                    name=record.name,
                    description=record.description,
                    created_on=record.created_on,
                )
                for record in records
            ]
        )
