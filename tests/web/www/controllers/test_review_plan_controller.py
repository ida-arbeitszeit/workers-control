from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.web.www.controllers.review_plan_controller import (
    ReviewDecision,
    ReviewPlanController,
)


class ReviewPlanControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ReviewPlanController)

    def test_that_approve_decision_is_returned_for_approve_form_value(self) -> None:
        request = FakeRequest()
        request.set_form("decision", "approve")
        assert self.controller.process_review_form(request) == ReviewDecision.approve

    def test_that_reject_decision_is_returned_for_reject_form_value(self) -> None:
        request = FakeRequest()
        request.set_form("decision", "reject")
        assert self.controller.process_review_form(request) == ReviewDecision.reject

    def test_that_none_is_returned_when_no_decision_is_provided(self) -> None:
        request = FakeRequest()
        assert self.controller.process_review_form(request) is None

    def test_that_none_is_returned_for_an_unknown_decision_value(self) -> None:
        request = FakeRequest()
        request.set_form("decision", "maybe")
        assert self.controller.process_review_form(request) is None

    def test_that_a_warning_is_displayed_when_no_valid_decision_is_provided(
        self,
    ) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        self.controller.process_review_form(request)
        assert self.notifier.warnings

    def test_that_no_warning_is_displayed_for_a_valid_decision(self) -> None:
        request = FakeRequest()
        request.set_form("decision", "approve")
        self.controller.process_review_form(request)
        assert not self.notifier.warnings
