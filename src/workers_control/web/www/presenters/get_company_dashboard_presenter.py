from __future__ import annotations

from dataclasses import dataclass

from workers_control.core.interactors.get_company_dashboard import (
    GetCompanyDashboardInteractor,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class GetCompanyDashboardPresenter:
    @dataclass
    class Tile:
        title: str
        subtitle: str
        icon: str
        url: str

    @dataclass
    class ViewModel:
        has_workers: bool
        company_name: str
        company_id: str
        company_email: str
        accounts_tile: GetCompanyDashboardPresenter.Tile

    url_index: UrlIndex
    translator: Translator

    def present(
        self, interactor_response: GetCompanyDashboardInteractor.Response
    ) -> ViewModel:
        return self.ViewModel(
            has_workers=interactor_response.has_workers,
            company_name=interactor_response.company_info.name,
            company_id=str(interactor_response.company_info.id),
            company_email=interactor_response.company_info.email,
            accounts_tile=self._create_accounts_tile(interactor_response),
        )

    def _create_accounts_tile(
        self, interactor_response: GetCompanyDashboardInteractor.Response
    ) -> Tile:
        return self.Tile(
            title=self.translator.gettext("Accounts"),
            subtitle=self.translator.gettext("You have four accounts"),
            icon="chart-line",
            url=self.url_index.get_company_accounts_url(
                company_id=interactor_response.company_info.id
            ),
        )
