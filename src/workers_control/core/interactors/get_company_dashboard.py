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
            email: str

        company_info: CompanyInfo
        has_workers: bool

    database_gateway: DatabaseGateway

    def get_dashboard(self, company_id: UUID) -> Response:
        record = (
            self.database_gateway.get_companies()
            .with_id(company_id)
            .joined_with_email_address()
            .first()
        )
        if record is None:
            raise self.Failure()
        company, email = record
        company_info = self.Response.CompanyInfo(
            id=company.id, name=company.name, email=email.address
        )
        has_workers = bool(
            self.database_gateway.get_members().working_at_company(company_id)
        )
        return self.Response(
            company_info=company_info,
            has_workers=has_workers,
        )
