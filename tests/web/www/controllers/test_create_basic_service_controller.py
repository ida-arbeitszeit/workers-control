from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceRequest,
)
from workers_control.web.www.controllers.create_basic_service_controller import (
    CreateBasicServiceController,
    InvalidRequest,
)


class FakeForm:
    def __init__(self, name: str = "test", description: str = "test desc") -> None:
        self._name = name
        self._description = description

    def get_name_string(self) -> str:
        return self._name

    def get_description_string(self) -> str:
        return self._description


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(CreateBasicServiceController)

    def test_anonymous_user_receives_401(self) -> None:
        self.session.logout()
        result = self.controller.import_form_data(FakeForm())
        assert isinstance(result, InvalidRequest)
        assert result.status_code == 401

    def test_logged_in_member_gets_interactor_request(self) -> None:
        member_id = uuid4()
        self.session.login_member(member_id)
        result = self.controller.import_form_data(FakeForm())
        assert isinstance(result, CreateBasicServiceRequest)

    def test_interactor_request_contains_member_id(self) -> None:
        member_id = uuid4()
        self.session.login_member(member_id)
        result = self.controller.import_form_data(FakeForm())
        assert isinstance(result, CreateBasicServiceRequest)
        assert result.member_id == member_id

    def test_interactor_request_contains_form_name(self) -> None:
        self.session.login_member(uuid4())
        result = self.controller.import_form_data(FakeForm(name="My Service"))
        assert isinstance(result, CreateBasicServiceRequest)
        assert result.name == "My Service"

    def test_interactor_request_contains_form_description(self) -> None:
        self.session.login_member(uuid4())
        result = self.controller.import_form_data(
            FakeForm(description="Service description")
        )
        assert isinstance(result, CreateBasicServiceRequest)
        assert result.description == "Service description"
