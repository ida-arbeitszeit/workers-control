from datetime import timedelta

from tests.datetime_service import datetime_min_utc
from workers_control.core.interactors import show_psf_account_details
from workers_control.core.records import SocialAccounting
from workers_control.core.transfers import TransferType

from .base_test_case import BaseTestCase


class InteractorTestBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_psf_account_details.ShowPSFAccountDetailsInteractor
        )
        self.psf_account = self.injector.get(SocialAccounting).account_psf


class PSFAccountBalanceTests(InteractorTestBase):
    def test_balance_is_zero_when_no_transfers_took_place(self) -> None:
        response = self.interactor.show_details()
        assert response.account_balance == 0

    def test_balance_is_non_zero_when_transfer_from_psf_account_took_place(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(debit_account=self.psf_account)
        response = self.interactor.show_details()
        assert response.account_balance != 0

    def test_balance_is_non_zero_when_transfer_to_psf_account_took_place(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(credit_account=self.psf_account)
        response = self.interactor.show_details()
        assert response.account_balance != 0


class PSFAccountTransferTests(InteractorTestBase):
    def test_no_transfers_returned_when_no_transfers_took_place(self) -> None:
        response = self.interactor.show_details()
        assert not response.transfers

    def test_that_no_transfers_are_returned_when_account_owner_is_neither_debitor_nor_creditor_of_transfer(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(
            debit_account=self.company_generator.create_company_record().means_account,
            credit_account=self.company_generator.create_company_record().means_account,
        )
        response = self.interactor.show_details()
        assert not response.transfers

    def test_that_transfer_is_returned_when_account_is_debit_account(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(debit_account=self.psf_account)
        response = self.interactor.show_details()
        assert response.transfers

    def test_that_transfer_is_returned_when_account_is_credit_account(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(credit_account=self.psf_account)
        response = self.interactor.show_details()
        assert response.transfers

    def test_two_transfers_are_recorded_in_descending_order(self) -> None:
        self.datetime_service.freeze_time(datetime_min_utc())
        self.transfer_generator.create_transfer(
            type=TransferType.taxes,
            credit_account=self.psf_account,
        )
        self.datetime_service.advance_time(timedelta(days=1))
        self.transfer_generator.create_transfer(
            type=TransferType.credit_public_a, debit_account=self.psf_account
        )
        response = self.interactor.show_details()
        assert response.transfers[0].type == TransferType.credit_public_a
        assert response.transfers[1].type == TransferType.taxes
