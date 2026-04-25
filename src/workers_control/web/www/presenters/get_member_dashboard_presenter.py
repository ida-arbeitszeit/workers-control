from dataclasses import dataclass
from typing import List

from workers_control.core.interactors import get_member_dashboard
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class Workplace:
    name: str
    url: str


@dataclass
class Invite:
    invite_details_url: str
    invite_message: str


@dataclass
class GetMemberDashboardViewModel:
    member_id: str
    account_balance: str
    email: str
    workplaces: List[Workplace]
    show_workplaces: bool
    show_workplace_registration_info: bool
    welcome_message: str
    invites: List[Invite]
    show_invites: bool


@dataclass
class GetMemberDashboardPresenter:
    translator: Translator
    url_index: UrlIndex

    def present(
        self, interactor_response: get_member_dashboard.Response
    ) -> GetMemberDashboardViewModel:
        invites = [
            self._get_invites_web(invite) for invite in interactor_response.invites
        ]
        return GetMemberDashboardViewModel(
            member_id=str(interactor_response.id),
            account_balance=self.translator.gettext(
                "%(num).2f hours" % dict(num=interactor_response.account_balance)
            ),
            email=interactor_response.email,
            workplaces=[
                Workplace(
                    name=workplace.workplace_name,
                    url=self.url_index.get_company_summary_url(
                        company_id=workplace.workplace_id
                    ),
                )
                for workplace in interactor_response.workplaces
            ],
            show_workplaces=bool(interactor_response.workplaces),
            show_workplace_registration_info=not bool(interactor_response.workplaces),
            welcome_message=self.translator.gettext("Welcome, %s!")
            % interactor_response.name,
            invites=invites,
            show_invites=bool(invites),
        )

    def _get_invites_web(self, invite: get_member_dashboard.WorkInvitation) -> Invite:
        return Invite(
            invite_details_url=self.url_index.get_work_invite_url(invite.invite_id),
            invite_message=self.translator.gettext(
                "Company %(company)s has invited you!"
                % dict(company=invite.company_name)
            ),
        )
