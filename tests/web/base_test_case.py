from tests.data_generators import (
    AccountantGenerator,
    BasicServiceGenerator,
    CompanyGenerator,
    MemberGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import TestingModule
from tests.lazy_property import LazyPropertyTestCase, _lazy_property
from tests.mail_service import MockEmailService
from tests.token import FakeTokenService
from tests.web.dependency_injection import WebTestsModule
from tests.web.email_configuration import FakeEmailConfiguration
from tests.web.email_presenters.text_renderer import TextRendererImpl
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


class BaseTestCase(LazyPropertyTestCase):
    "Web unit tests should inherit from this class."

    def setUp(self) -> None:
        super().setUp()
        self.injector = Injector(modules=[TestingModule(), WebTestsModule()])

    # It would be nice to have the following list sorted
    # alphabetically
    accountant_generator = _lazy_property(AccountantGenerator)
    basic_service_generator = _lazy_property(BasicServiceGenerator)
    company_generator = _lazy_property(CompanyGenerator)
    datetime_service = _lazy_property(FakeDatetimeService)
    datetime_formatter = _lazy_property(FakeDatetimeFormatter)
    timezone_configuration = _lazy_property(FakeTimezoneConfiguration)
    email_configuration = _lazy_property(FakeEmailConfiguration)
    email_service = _lazy_property(MockEmailService)
    member_generator = _lazy_property(MemberGenerator)
    notifier = _lazy_property(NotifierTestImpl)
    request = _lazy_property(FakeRequest)
    session = _lazy_property(FakeSession)
    text_renderer = _lazy_property(TextRendererImpl)
    token_service = _lazy_property(FakeTokenService)
    translator = _lazy_property(FakeTranslator)
    url_index = _lazy_property(UrlIndexTestImpl)
