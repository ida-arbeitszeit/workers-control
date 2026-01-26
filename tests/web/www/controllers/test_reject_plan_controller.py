from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.controllers.reject_plan_controller import (
    RejectPlanController,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RejectPlanController)

    def test_that_provided_plan_id_is_used_in_request(self) -> None:
        expected_plan_id = uuid4()
        request = self.controller.reject_plan(plan=expected_plan_id)
        self.assertEqual(request.plan, expected_plan_id)
