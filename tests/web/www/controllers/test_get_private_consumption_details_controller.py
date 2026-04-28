from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.get_private_consumption_details_controller import (
    GetPrivateConsumptionDetailsController,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(GetPrivateConsumptionDetailsController)

    def test_request_contains_consumption_id_passed_in(self) -> None:
        self.session.login_member(uuid4())
        expected_consumption_id = uuid4()
        request = self.controller.create_request(consumption_id=expected_consumption_id)
        assert request.consumption_id == expected_consumption_id

    def test_request_contains_logged_in_member_id(self) -> None:
        expected_member_id = uuid4()
        self.session.login_member(expected_member_id)
        request = self.controller.create_request(consumption_id=uuid4())
        assert request.member == expected_member_id

    def test_assertion_error_is_raised_when_no_user_is_logged_in(self) -> None:
        self.session.logout()
        with self.assertRaises(AssertionError):
            self.controller.create_request(consumption_id=uuid4())
