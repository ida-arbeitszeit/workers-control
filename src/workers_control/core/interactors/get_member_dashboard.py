from dataclasses import dataclass
from typing import List
from uuid import UUID

from workers_control.core.records import CompanyWorkInvite
from workers_control.core.repositories import DatabaseGateway


@dataclass
class Request:
    member: UUID


@dataclass
class Workplace:
    workplace_name: str
    workplace_id: UUID


@dataclass
class WorkInvitation:
    invite_id: UUID
    company_id: UUID
    company_name: str


@dataclass
class Response:
    workplaces: List[Workplace]
    invites: List[WorkInvitation]
    name: str


@dataclass
class GetMemberDashboardInteractor:
    database_gateway: DatabaseGateway

    def get_member_dashboard(self, request: Request) -> Response:
        member = self.database_gateway.get_members().with_id(request.member).first()
        assert member
        return Response(
            workplaces=self._get_workplaces(request.member),
            invites=self._get_invites(request.member),
            name=member.name,
        )

    def _get_workplaces(self, member: UUID) -> List[Workplace]:
        return [
            Workplace(
                workplace_name=company.name,
                workplace_id=company.id,
            )
            for company in self.database_gateway.get_companies().that_are_workplace_of_member(
                member
            )
        ]

    def _get_invites(self, member: UUID) -> List[WorkInvitation]:
        return [
            self._render_company_work_invite(invite)
            for invite in self.database_gateway.get_company_work_invites().addressing(
                member
            )
        ]

    def _render_company_work_invite(self, invite: CompanyWorkInvite) -> WorkInvitation:
        company = self.database_gateway.get_companies().with_id(invite.company).first()
        assert company
        return WorkInvitation(
            invite_id=invite.id,
            company_id=invite.company,
            company_name=company.name,
        )
