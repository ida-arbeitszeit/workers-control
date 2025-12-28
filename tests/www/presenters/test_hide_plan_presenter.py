from uuid import uuid4

from tests.www.base_test_case import BaseTestCase
from workers_control.core.interactors.hide_plan import HidePlanResponse
from workers_control.web.www.presenters.hide_plan_presenter import HidePlanPresenter

SUCCESSFUL_DELETE_RESPONSE = HidePlanResponse(
    plan_id=uuid4(),
    is_success=True,
)
FAILED_DELETE_RESPONSE = HidePlanResponse(
    plan_id=uuid4(),
    is_success=False,
)


class HidePlanPresenterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.presenter = self.injector.get(HidePlanPresenter)

    def test_that_a_notification_is_shown_when_deletion_was_successful(self):
        self.presenter.present(SUCCESSFUL_DELETE_RESPONSE)
        self.assertTrue(self.notifier.infos)

    def test_that_no_notification_is_shown_when_deletion_was_a_failure(self):
        self.presenter.present(FAILED_DELETE_RESPONSE)
        self.assertFalse(self.notifier.infos)
