from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import (
    AccountantGenerator,
    BasicServiceGenerator,
    CompanyGenerator,
    ConsumptionGenerator,
    CooperationGenerator,
    CoordinationTenureGenerator,
    CoordinationTransferRequestGenerator,
    MemberGenerator,
    PlanGenerator,
    RegisteredHoursWorkedGenerator,
    TransferGenerator,
    WorkerAffiliationGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import TestingModule
from tests.economic_scenarios import EconomicScenarios
from tests.email_notifications import EmailSenderTestImpl
from tests.lazy_property import LazyPropertyTestCase, _lazy_property
from workers_control.core.injector import Injector
from workers_control.core.repositories import DatabaseGateway

from .balance_checker import BalanceChecker
from .price_checker import PriceChecker


class BaseTestCase(LazyPropertyTestCase):
    "Interactor unit tests should inherit from this class."

    def setUp(self) -> None:
        super().setUp()
        self.injector = Injector([TestingModule()])

    # It would be nice to have the following list sorted
    # alphabetically
    accountant_generator = _lazy_property(AccountantGenerator)
    balance_checker = _lazy_property(BalanceChecker)
    basic_service_generator = _lazy_property(BasicServiceGenerator)
    company_generator = _lazy_property(CompanyGenerator)
    consumption_generator = _lazy_property(ConsumptionGenerator)
    control_thresholds = _lazy_property(ControlThresholdsTestImpl)
    cooperation_generator = _lazy_property(CooperationGenerator)
    coordination_tenure_generator = _lazy_property(CoordinationTenureGenerator)
    coordination_transfer_request_generator = _lazy_property(
        CoordinationTransferRequestGenerator
    )
    database_gateway = _lazy_property(DatabaseGateway)
    datetime_service = _lazy_property(FakeDatetimeService)
    economic_scenarios = _lazy_property(EconomicScenarios)
    email_sender = _lazy_property(EmailSenderTestImpl)
    member_generator = _lazy_property(MemberGenerator)
    plan_generator = _lazy_property(PlanGenerator)
    price_checker = _lazy_property(PriceChecker)
    registered_hours_worked_generator = _lazy_property(RegisteredHoursWorkedGenerator)
    transfer_generator = _lazy_property(TransferGenerator)
    worker_affiliation_generator = _lazy_property(WorkerAffiliationGenerator)
