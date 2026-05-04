from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.deactivate_basic_service import (
    RejectionReason,
    Response,
)
from workers_control.web.www.presenters.deactivate_basic_service_presenter import (
    DeactivateBasicServicePresenter,
)

SUCCESSFUL_RESPONSE = Response(rejection_reason=None)
NOT_FOUND_RESPONSE = Response(
    rejection_reason=RejectionReason.service_not_found,
)
ALREADY_DEACTIVATED_RESPONSE = Response(
    rejection_reason=RejectionReason.already_deactivated,
)


class DeactivateBasicServicePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(DeactivateBasicServicePresenter)

    def test_an_info_notification_is_shown_on_success(self) -> None:
        self.presenter.present(SUCCESSFUL_RESPONSE)
        self.assertTrue(self.notifier.infos)

    def test_no_warning_is_shown_on_success(self) -> None:
        self.presenter.present(SUCCESSFUL_RESPONSE)
        self.assertFalse(self.notifier.warnings)

    def test_a_warning_is_shown_when_service_was_not_found(self) -> None:
        self.presenter.present(NOT_FOUND_RESPONSE)
        self.assertTrue(self.notifier.warnings)

    def test_no_info_notification_is_shown_when_service_was_not_found(self) -> None:
        self.presenter.present(NOT_FOUND_RESPONSE)
        self.assertFalse(self.notifier.infos)

    def test_a_warning_is_shown_when_service_was_already_deactivated(self) -> None:
        self.presenter.present(ALREADY_DEACTIVATED_RESPONSE)
        self.assertTrue(self.notifier.warnings)
