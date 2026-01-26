from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.show_prd_account_details_controller import (
    ShowPRDAccountDetailsController,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowPRDAccountDetailsController)

    def test_company_id_is_returned_unchanged_as_interactor_request(
        self,
    ) -> None:
        expected_company = uuid4()
        interactor_request = self.controller.create_request(company=expected_company)
        assert interactor_request.company_id == expected_company
