from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from workers_control.core import records
from workers_control.core.repositories import DatabaseGateway


@dataclass
class QueriedBasicService:
    id: UUID
    name: str
    description: str
    provider_name: str
    created_on: datetime


@dataclass
class QueryBasicServicesRequest:
    query_string: Optional[str]
    offset: Optional[int] = None
    limit: Optional[int] = None


@dataclass
class QueryBasicServicesResponse:
    results: list[QueriedBasicService]
    total_results: int
    request: QueryBasicServicesRequest


@dataclass
class QueryBasicServicesInteractor:
    database_gateway: DatabaseGateway

    def execute(self, request: QueryBasicServicesRequest) -> QueryBasicServicesResponse:
        basic_services = self.database_gateway.get_basic_services()
        if request.query_string is not None:
            basic_services = basic_services.with_name_containing(request.query_string)
        total_results = len(basic_services)
        basic_services = basic_services.ordered_by_creation_date(ascending=False)
        joined = basic_services.joined_with_provider()
        if request.offset is not None:
            joined = joined.offset(n=request.offset)
        if request.limit is not None:
            joined = joined.limit(n=request.limit)
        results = [
            self._to_response_model(basic_service, provider)
            for basic_service, provider in joined
        ]
        return QueryBasicServicesResponse(
            results=results,
            total_results=total_results,
            request=request,
        )

    def _to_response_model(
        self,
        basic_service: records.BasicService,
        provider: records.Member,
    ) -> QueriedBasicService:
        return QueriedBasicService(
            id=basic_service.id,
            name=basic_service.name,
            description=basic_service.description,
            provider_name=provider.name,
            created_on=basic_service.created_on,
        )
