from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.decimal import decimal_sum
from workers_control.core.records import ProductionCosts, SocialAccounting
from workers_control.core.services.payout_factor import PayoutFactorService
from workers_control.core.services.psf_balance import PublicSectorFundService


class PsfBaseTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PublicSectorFundService)
        self.psf_account = self.injector.get(SocialAccounting).account_psf


class TransferBasedTests(PsfBaseTest):
    @parameterized.expand(
        [
            ([Decimal(0)], [Decimal(0)]),
            ([Decimal(10), Decimal(15)], [Decimal(10)]),
            ([Decimal(5)], [Decimal(10), Decimal(10), Decimal(10)]),
            ([Decimal(5.11)], [Decimal(10.22), Decimal(10.3333), Decimal(10.4444)]),
        ]
    )
    def test_that_psf_balance_equals_difference_of_summed_up_transfers(
        self,
        inbound_transfer_values: list[Decimal],
        outbound_transfer_values: list[Decimal],
    ) -> None:
        for t in inbound_transfer_values:
            self.transfer_generator.create_transfer(
                credit_account=self.psf_account, value=t
            )
        for t in outbound_transfer_values:
            self.transfer_generator.create_transfer(
                debit_account=self.psf_account, value=t
            )
        expected_balance = decimal_sum(inbound_transfer_values) - decimal_sum(
            outbound_transfer_values
        )
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == expected_balance


class PsfBalanceScenarioTests(PsfBaseTest):
    def test_that_without_plans_the_account_is_balanced(self) -> None:
        psf_balance = self.service.calculate_psf_balance()
        self.assertEqual(psf_balance, 0)

    def test_that_with_productive_plan_the_account_is_balanced(self) -> None:
        self.plan_generator.create_plan()
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    def test_that_public_plan_leads_to_negative_balance(self) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance < Decimal(0)

    def test_that_no_plans_and_registered_work_lead_to_balanced_account(
        self,
    ) -> None:
        self._register_hours_worked(Decimal(10))
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    def test_that_productive_plan_and_registered_work_lead_to_balanced_account(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        self._register_hours_worked(Decimal(10))
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    @parameterized.expand(
        [
            (
                Decimal(100),
                Decimal(10),
            ),
            (
                Decimal(100),
                Decimal(0),
            ),
        ]
    )
    def test_that_account_is_balanced_when_fic_is_larger_than_zero_and_all_labour_has_been_registered(
        self,
        labour_in_productive_sector: Decimal,
        labour_in_public_sector: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(labour_in_productive_sector),
                resource_cost=Decimal(1),
                means_cost=Decimal(1),
            ),
        )
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(labour_in_public_sector),
                resource_cost=Decimal(1),
                means_cost=Decimal(1),
            ),
        )
        assert self._calculate_payout_factor() > 0

        self._register_hours_worked(
            labour_in_productive_sector + labour_in_public_sector
        )

        psf_balance = self.service.calculate_psf_balance()
        self.assertAlmostEqual(psf_balance, 0)

    @parameterized.expand(
        [
            (
                Decimal(100),
                Decimal(10),
            ),
            (
                Decimal(100),
                Decimal(0),
            ),
        ]
    )
    def test_that_balance_is_negative_when_fic_is_larger_than_zero_and_not_all_labour_has_been_registered(
        self,
        labour_in_productive_sector: Decimal,
        labour_in_public_sector: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(labour_in_productive_sector),
                resource_cost=Decimal(1),
                means_cost=Decimal(1),
            ),
        )
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(labour_in_public_sector),
                resource_cost=Decimal(1),
                means_cost=Decimal(1),
            ),
        )
        assert self._calculate_payout_factor() > 0

        self._register_hours_worked(
            (labour_in_productive_sector + labour_in_public_sector) / 2,
        )
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance < 0

    @parameterized.expand(
        [
            (Decimal(0), Decimal(1)),
            (Decimal(0.1), Decimal(9)),
            (Decimal(0.5), Decimal(1)),
            (Decimal(0.8), Decimal(0.5)),
        ]
    )
    def test_that_balance_grows_if_payout_factor_is_smaller_than_one_and_worked_hours_are_registered(
        self, payout_factor: Decimal, hours_worked: Decimal
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(payout_factor)
        psf_balance_before = self.service.calculate_psf_balance()
        self._register_hours_worked(hours_worked)
        psf_balance_after = self.service.calculate_psf_balance()
        assert psf_balance_after > psf_balance_before
        self.assertAlmostEqual(
            psf_balance_after, psf_balance_before + (hours_worked * (1 - payout_factor))
        )

    @parameterized.expand(
        [
            (Decimal(10)),
            (Decimal(100)),
            (Decimal(1000)),
        ]
    )
    def test_that_balance_stays_the_same_if_payout_factor_is_one_and_worked_hours_are_registered(
        self, hours_worked: Decimal
    ) -> None:
        fic = Decimal(1)
        self.economic_scenarios.setup_environment_with_fic(fic)
        psf_balance_before = self.service.calculate_psf_balance()
        self._register_hours_worked(hours_worked)
        psf_balance_after = self.service.calculate_psf_balance()
        assert psf_balance_after == psf_balance_before

    def _register_hours_worked(
        self,
        hours_worked: Decimal,
        company: UUID | None = None,
        worker: UUID | None = None,
    ) -> None:
        worker = worker or self.member_generator.create_member()
        company = company or self.company_generator.create_company(workers=[worker])
        self.registered_hours_worked_generator.register_hours_worked(
            company=company, worker=worker, hours=hours_worked
        )

    def _calculate_payout_factor(self) -> Decimal:
        service = self.injector.get(PayoutFactorService)
        return service.calculate_current_payout_factor()
