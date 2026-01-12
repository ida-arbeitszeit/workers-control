from dataclasses import dataclass

from workers_control.core.interactors.show_psf_account_details import (
    ShowPSFAccountDetailsInteractor,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem
from workers_control.web.www.presenters.transfers import (
    TransferInfo,
    TransferPresenter,
)


@dataclass
class ShowPSFAccountDetailsPresenter:
    @dataclass
    class ViewModel:
        transfers: list[TransferInfo]
        account_balance: str
        navbar_items: list[NavbarItem]

    transfer_presenter: TransferPresenter
    translator: Translator
    url_index: UrlIndex

    def present(
        self, interactor_response: ShowPSFAccountDetailsInteractor.Response
    ) -> ViewModel:
        transfers = self.transfer_presenter.present_transfers(
            interactor_response.transfers
        )
        return self.ViewModel(
            transfers=transfers,
            account_balance=str(round(interactor_response.account_balance, 2)),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Global statistics"),
                    url=self.url_index.get_global_statistics_url(),
                ),
                NavbarItem(
                    text=self.translator.gettext("Account PSF"),
                    url=None,
                ),
            ],
        )
