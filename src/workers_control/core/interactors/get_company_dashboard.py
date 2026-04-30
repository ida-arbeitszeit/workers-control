from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from workers_control.core.repositories import DatabaseGateway


@dataclass
class GetCompanyDashboardInteractor:
    class Failure(Exception):
        pass

    @dataclass
    class Response:
        @dataclass
        class CompanyInfo:
            id: UUID
            name: str

        company_info: CompanyInfo

    database_gateway: DatabaseGateway

    def get_dashboard(self, company_id: UUID) -> Response:
        company = self.database_gateway.get_companies().with_id(company_id).first()
        if company is None:
            raise self.Failure()
        company_info = self.Response.CompanyInfo(
            id=company.id,
            name=company.name,
        )
        return self.Response(
            company_info=company_info,
        )
