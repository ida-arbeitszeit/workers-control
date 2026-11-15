from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from workers_control.web.session import Session, UserRole
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class NavbarItem:
    text: str
    url: Optional[str]


@dataclass
class CompanyNavbarItems:
    session: Session
    url_index: UrlIndex
    translator: Translator

    def for_company_summary(
        self, company_id: UUID, company_name: str
    ) -> list[NavbarItem]:
        if self._is_own_company(company_id):
            return [
                NavbarItem(text=self.translator.gettext("Company overview"), url=None)
            ]
        return [
            self._all_companies_item(),
            NavbarItem(text=company_name, url=None),
        ]

    def for_company_account(
        self, company_id: UUID, company_name: str, account_label: str
    ) -> list[NavbarItem]:
        current_page = NavbarItem(text=account_label, url=None)
        if self._is_own_company(company_id):
            return [
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(company_id=company_id),
                ),
                current_page,
            ]
        return self._company_trail(company_id, company_name) + [current_page]

    def for_plan(
        self, planner_id: UUID, planner_name: str, plan_name: str
    ) -> list[NavbarItem]:
        current_page = NavbarItem(text=plan_name, url=None)
        if self._is_own_company(planner_id):
            return [
                NavbarItem(
                    text=self.translator.gettext("My plans"),
                    url=self.url_index.get_my_plans_url(),
                ),
                current_page,
            ]
        return self._company_trail(planner_id, planner_name) + [current_page]

    def _company_trail(self, company_id: UUID, company_name: str) -> list[NavbarItem]:
        return [
            self._all_companies_item(),
            NavbarItem(
                text=company_name,
                url=self.url_index.get_company_summary_url(company_id=company_id),
            ),
        ]

    def _is_own_company(self, company_id: UUID) -> bool:
        return (
            self.session.get_user_role() == UserRole.company
            and self.session.get_current_user() == company_id
        )

    def _all_companies_item(self) -> NavbarItem:
        return NavbarItem(
            text=self.translator.gettext("All companies"),
            url=self.url_index.get_query_companies_url(),
        )
