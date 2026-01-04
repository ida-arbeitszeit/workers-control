from dataclasses import dataclass

from workers_control.core.interactors.show_psf_account_details import (
    ShowPSFAccountDetailsInteractor,
)
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

    transfer_presenter: TransferPresenter

    def present(
        self, interactor_response: ShowPSFAccountDetailsInteractor.Response
    ) -> ViewModel:
        transfers = self.transfer_presenter.present_transfers(
            interactor_response.transfers
        )
        return self.ViewModel(
            transfers=transfers,
            account_balance=str(round(interactor_response.account_balance, 2)),
        )
