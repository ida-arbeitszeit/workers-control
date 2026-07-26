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
from tests.mail_service import MockEmailService
from tests.token import FakeTokenService
from tests.web.email_configuration import FakeEmailConfiguration
from tests.web.email_presenters.text_renderer import TextRendererTestImpl
from tests.web.www.datetime_formatter import (
    FakeDatetimeFormatter,
    FakeTimezoneConfiguration,
)
from tests.web.www.presenters.notifier import NotifierTestImpl
from tests.web.www.presenters.url_index import UrlIndexTestImpl
from tests.web.www.request import FakeRequest
from tests.web.www.session import FakeSession
from tests.web.www.translator import FakeTranslator
from workers_control.core.injector import Injector
from workers_control.core.repositories import DatabaseGateway

from .interactors.balance_checker import BalanceChecker
from .interactors.price_checker import PriceChecker


class BaseTestCase(LazyPropertyTestCase):
    "Interactor and web unit tests should inherit from this class."

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
    datetime_formatter = _lazy_property(FakeDatetimeFormatter)
    datetime_service = _lazy_property(FakeDatetimeService)
    economic_scenarios = _lazy_property(EconomicScenarios)
    email_configuration = _lazy_property(FakeEmailConfiguration)
    email_sender = _lazy_property(EmailSenderTestImpl)
    email_service = _lazy_property(MockEmailService)
    member_generator = _lazy_property(MemberGenerator)
    notifier = _lazy_property(NotifierTestImpl)
    plan_generator = _lazy_property(PlanGenerator)
    price_checker = _lazy_property(PriceChecker)
    registered_hours_worked_generator = _lazy_property(RegisteredHoursWorkedGenerator)
    request = _lazy_property(FakeRequest)
    session = _lazy_property(FakeSession)
    text_renderer = _lazy_property(TextRendererTestImpl)
    timezone_configuration = _lazy_property(FakeTimezoneConfiguration)
    token_service = _lazy_property(FakeTokenService)
    transfer_generator = _lazy_property(TransferGenerator)
    translator = _lazy_property(FakeTranslator)
    worker_affiliation_generator = _lazy_property(WorkerAffiliationGenerator)
    url_index = _lazy_property(UrlIndexTestImpl)
