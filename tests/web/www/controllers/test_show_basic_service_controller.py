from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.show_basic_service_controller import (
    ShowBasicServiceController,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowBasicServiceController)

    def test_basic_service_id_is_returned_unchanged_as_interactor_request(
        self,
    ) -> None:
        expected_id = uuid4()
        interactor_request = self.controller.create_request(
            basic_service_id=expected_id
        )
        assert interactor_request.basic_service_id == expected_id
