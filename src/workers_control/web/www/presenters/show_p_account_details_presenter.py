from dataclasses import dataclass
from typing import List

from workers_control.core.interactors.show_p_account_details import (
    ShowPAccountDetailsInteractor,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import CompanyNavbarItems, NavbarItem
from workers_control.web.www.presenters.transfers import (
    TransferInfo,
    TransferPresenter,
)


@dataclass
class ShowPAccountDetailsPresenter:
    @dataclass
    class ViewModel:
        transfers: List[TransferInfo]
        account_balance: str
        plot_url: str
        navbar_items: list[NavbarItem]

    translator: Translator
    url_index: UrlIndex
    transfer_presenter: TransferPresenter
    company_navbar_items: CompanyNavbarItems

    def present(
        self, interactor_response: ShowPAccountDetailsInteractor.Response
    ) -> ViewModel:
        transfers = self.transfer_presenter.present_transfers(
            interactor_response.transfers
        )
        return self.ViewModel(
            transfers=transfers,
            account_balance=str(round(interactor_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_p_account(
                interactor_response.company_id
            ),
            navbar_items=self.company_navbar_items.for_company_account(
                company_id=interactor_response.company_id,
                company_name=interactor_response.company_name,
                account_label=self.translator.gettext("Account p"),
            ),
        )
