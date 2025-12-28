from uuid import uuid4

from tests.www.base_test_case import BaseTestCase
from workers_control.web.www.controllers.show_a_account_details_controller import (
    ShowAAccountDetailsController,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowAAccountDetailsController)

    def test_company_id_is_returned_unchanged_as_interactor_request(
        self,
    ) -> None:
        expected_company = uuid4()
        interactor_request = self.controller.create_request(company=expected_company)
        assert interactor_request.company == expected_company
