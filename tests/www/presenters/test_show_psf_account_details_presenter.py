from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from parameterized import parameterized

from tests.datetime_service import datetime_min_utc
from tests.www.base_test_case import BaseTestCase
from workers_control.core.interactors.show_psf_account_details import (
    ShowPSFAccountDetailsInteractor,
)
from workers_control.core.services.account_details import (
    AccountTransfer,
    TransferParty,
    TransferPartyType,
)
from workers_control.core.transfers import TransferType
from workers_control.web.www.presenters.show_psf_account_details_presenter import (
    ShowPSFAccountDetailsPresenter,
)


class ShowPSFAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPSFAccountDetailsPresenter)

    def test_return_empty_list_when_no_transfers_took_place(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transfers, [])

    def test_return_correct_info_when_one_transfer_took_place(self) -> None:
        EXPECTED_ACCOUNT_BALANCE = Decimal(100.007)
        transfer = self.get_transfer_info()
        response = self.get_interactor_response(
            transfers=[transfer], account_balance=EXPECTED_ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 1)
        self.assertEqual(
            view_model.account_balance, str(round(EXPECTED_ACCOUNT_BALANCE, 2))
        )
        assert len(view_model.transfers) == 1
        view_model_transfer = view_model.transfers[0]
        self.assertEqual(
            view_model_transfer.date,
            self.datetime_formatter.format_datetime(
                date=transfer.date, fmt="%d.%m.%Y %H:%M"
            ),
        )
        self.assertEqual(
            view_model_transfer.transfer_volume, str(round(transfer.volume, 2))
        )

    @parameterized.expand(
        [
            (
                TransferType.taxes,
                "Contribution to public sector",
            ),
            (
                TransferType.credit_public_a,
                "Planned labour (public plan)",
            ),
            (
                TransferType.credit_public_p,
                "Planned fixed means of production (public plan)",
            ),
            (
                TransferType.credit_public_r,
                "Planned liquid means of production (public plan)",
            ),
        ]
    )
    def test_that_type_of_transfer_is_converted_into_correct_string(
        self, transfer_type: TransferType, expected_string: str
    ) -> None:
        transfer = self.get_transfer_info(type=transfer_type)
        response = self.get_interactor_response(transfers=[transfer])
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].transfer_type == (
            self.translator.gettext(expected_string)
        )

    @parameterized.expand([(True,), (False,)])
    def test_that_debit_transfer_are_shown_as_such(
        self,
        is_debit: bool,
    ) -> None:
        response = self.get_interactor_response(
            transfers=[self.get_transfer_info(is_debit_transfer=is_debit)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].is_debit_transfer == is_debit

    def test_return_two_transfers_when_two_transfers_took_place(self) -> None:
        response = self.get_interactor_response(
            transfers=[self.get_transfer_info(), self.get_transfer_info()],
            account_balance=Decimal(100),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 2)

    def get_transfer_info(
        self,
        type: TransferType = TransferType.taxes,
        date: datetime = datetime_min_utc(),
        volume: Decimal = Decimal(10.002),
        is_debit_transfer: bool = False,
    ) -> AccountTransfer:
        return AccountTransfer(
            type=type,
            date=date,
            volume=volume,
            is_debit_transfer=is_debit_transfer,
            debtor_equals_creditor=False,
            transfer_party=TransferParty(
                type=TransferPartyType.member,
                id=uuid4(),
                name="Some counter party name",
            ),
        )

    def get_interactor_response(
        self,
        transfers: list[AccountTransfer] | None = None,
        account_balance: Decimal = Decimal(0),
    ) -> ShowPSFAccountDetailsInteractor.Response:
        if transfers is None:
            transfers = []
        return ShowPSFAccountDetailsInteractor.Response(
            transfers=transfers,
            account_balance=account_balance,
        )


class NavbarTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPSFAccountDetailsPresenter)

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_leads_to_statistics(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[0]
        assert navbar_item.text == self.translator.gettext("Global statistics")
        assert navbar_item.url == self.url_index.get_global_statistics_url()

    def test_second_navbar_item_has_text_account_psf_and_no_url(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account PSF")
        assert navbar_item.url is None

    def get_interactor_response(
        self,
    ) -> ShowPSFAccountDetailsInteractor.Response:
        return ShowPSFAccountDetailsInteractor.Response(
            transfers=[],
            account_balance=Decimal(0),
        )
