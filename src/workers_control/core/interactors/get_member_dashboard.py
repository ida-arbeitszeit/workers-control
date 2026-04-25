from dataclasses import dataclass
from decimal import Decimal
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
    account_balance: Decimal
    name: str
    email: str
    id: UUID


@dataclass
class GetMemberDashboardInteractor:
    database_gateway: DatabaseGateway

    def get_member_dashboard(self, request: Request) -> Response:
        record = (
            self.database_gateway.get_members()
            .with_id(request.member)
            .joined_with_email_address()
            .first()
        )
        assert record
        _member, email = record
        return Response(
            workplaces=self._get_workplaces(request.member),
            invites=self._get_invites(request.member),
            account_balance=self._get_account_balance(request.member),
            name=_member.name,
            email=email.address,
            id=_member.id,
        )

    def _get_account_balance(self, member: UUID) -> Decimal:
        result = (
            self.database_gateway.get_accounts()
            .owned_by_member(member)
            .joined_with_balance()
            .first()
        )
        assert result
        return result[1]

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
