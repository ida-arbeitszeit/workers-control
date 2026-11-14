from datetime import datetime
from decimal import Decimal
from typing import Callable, List
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_min_utc
from tests.web.www.session import FakeSession
from tests.web.www.translator import FakeTranslator
from workers_control.core.interactors import show_r_account_details
from workers_control.core.services.account_details import (
    AccountTransfer,
    PlotDetails,
    TransferParty,
    TransferPartyType,
)
from workers_control.core.transfers import TransferType
from workers_control.web.www.navbar import NavbarItem
from workers_control.web.www.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)


class ShowRAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.trans = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(ShowRAccountDetailsPresenter)

    def test_return_empty_list_when_no_transfers_took_place(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert not view_model.transfers

    def test_return_correct_info_when_one_transfer_took_place(self) -> None:
        EXPECTED_ACCOUNT_BALANCE = Decimal(100.007)
        EXPECTED_DATE = datetime_min_utc()
        EXPECTED_TYPE = TransferType.credit_r
        EXPECTED_VOLUME = Decimal(10.007)
        response = self.get_interactor_response(
            transfers=[
                self.get_transfer_info(
                    date=EXPECTED_DATE,
                    type=EXPECTED_TYPE,
                    volume=EXPECTED_VOLUME,
                )
            ],
            account_balance=EXPECTED_ACCOUNT_BALANCE,
        )
        view_model = self.presenter.present(response)
        assert len(view_model.transfers) == 1
        assert view_model.account_balance == str(round(EXPECTED_ACCOUNT_BALANCE, 2))
        transfer = view_model.transfers[0]
        assert transfer.date == self.datetime_formatter.format_datetime(
            date=EXPECTED_DATE, fmt="%d.%m.%Y %H:%M"
        )
        assert transfer.transfer_volume == str(round(EXPECTED_VOLUME, 2))

    @parameterized.expand(
        [
            (
                TransferType.credit_r,
                "Planned liquid means of production",
            ),
            (
                TransferType.productive_consumption_r,
                "Productive consumption of liquid means of production",
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
            transfers=[self.get_transfer_info(is_debit=is_debit)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].is_debit_transfer == is_debit

    def test_return_two_transfers_when_two_transfers_took_place(self) -> None:
        response = self.get_interactor_response(
            transfers=[
                self.get_transfer_info(),
                self.get_transfer_info(),
            ],
            account_balance=Decimal(100),
        )
        view_model = self.presenter.present(response)
        assert len(view_model.transfers) == 2

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert view_model.plot_url
        assert str(response.company_id) in view_model.plot_url

    def test_company_viewing_own_account_sees_accounts_as_parent_page(self) -> None:
        response = self.get_interactor_response()
        self.session.login_company(response.company_id)
        view_model = self.presenter.present(response)
        assert view_model.navbar_items == [
            NavbarItem(
                text=self.translator.gettext("Accounts"),
                url=self.url_index.get_company_accounts_url(
                    company_id=response.company_id
                ),
            ),
            NavbarItem(text=self.translator.gettext("Account r"), url=None),
        ]

    @parameterized.expand(
        [
            (FakeSession.login_company,),
            (FakeSession.login_member,),
            (FakeSession.login_accountant,),
        ]
    )
    def test_other_users_see_all_companies_and_company_as_parent_pages(
        self, log_in: Callable[[FakeSession, UUID], None]
    ) -> None:
        response = self.get_interactor_response(company_name="Bakery")
        log_in(self.session, uuid4())
        view_model = self.presenter.present(response)
        assert view_model.navbar_items == [
            NavbarItem(
                text=self.translator.gettext("All companies"),
                url=self.url_index.get_query_companies_url(),
            ),
            NavbarItem(
                text="Bakery",
                url=self.url_index.get_company_summary_url(
                    company_id=response.company_id
                ),
            ),
            NavbarItem(text=self.translator.gettext("Account r"), url=None),
        ]

    def get_transfer_info(
        self,
        type: TransferType = TransferType.credit_r,
        date: datetime | None = None,
        volume: Decimal = Decimal(10),
        is_debit: bool = False,
    ) -> AccountTransfer:
        if date is None:
            date = datetime_min_utc()
        return AccountTransfer(
            type=type,
            date=date,
            volume=volume,
            is_debit_transfer=is_debit,
            transfer_party=TransferParty(
                type=TransferPartyType.company,
                id=uuid4(),
                name="Some counter party name",
            ),
            debtor_equals_creditor=False,
        )

    def get_interactor_response(
        self,
        company_id: UUID = uuid4(),
        company_name: str = "Some company",
        transfers: List[show_r_account_details.AccountTransfer] | None = None,
        account_balance: Decimal = Decimal(0),
        plot: PlotDetails | None = None,
    ) -> show_r_account_details.Response:
        if transfers is None:
            transfers = []
        if plot is None:
            plot = PlotDetails([], [])
        return show_r_account_details.Response(
            company_id=company_id,
            company_name=company_name,
            transfers=transfers,
            account_balance=account_balance,
            plot=plot,
        )
