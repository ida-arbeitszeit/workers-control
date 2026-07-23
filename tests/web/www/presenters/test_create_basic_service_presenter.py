from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceResponse,
)
from workers_control.web.www.presenters.create_basic_service_presenter import (
    CreateBasicServicePresenter,
)

SUCCESSFUL_CREATE_RESPONSE = CreateBasicServiceResponse(
    rejection_reason=None, basic_service_id=uuid4()
)

REJECTED_RESPONSE_MEMBER_NOT_FOUND = CreateBasicServiceResponse(
    rejection_reason=CreateBasicServiceResponse.RejectionReason.member_not_found,
    basic_service_id=None,
)


class CreateBasicServicePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateBasicServicePresenter)

    def test_info_notification_returned_when_creation_was_successful(self) -> None:
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertTrue(self._get_info_notifications())

    def test_correct_info_notification_returned_when_creation_was_successful(
        self,
    ) -> None:
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertIn(
            self.translator.gettext("Successfully created basic service."),
            self._get_info_notifications(),
        )

    def test_warning_notification_returned_when_creation_was_rejected_because_member_not_found(
        self,
    ) -> None:
        self.presenter.present(REJECTED_RESPONSE_MEMBER_NOT_FOUND)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_warning_notification_is_returned_when_creation_was_rejected_because_member_not_found(
        self,
    ) -> None:
        self.presenter.present(REJECTED_RESPONSE_MEMBER_NOT_FOUND)
        self.assertIn(
            self.translator.gettext("Basic service creation failed: Member not found."),
            self._get_warning_notifications(),
        )

    def _get_info_notifications(self) -> list[str]:
        return self.notifier.infos

    def _get_warning_notifications(self) -> list[str]:
        return self.notifier.warnings


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateBasicServicePresenter)

    def test_navbar_shows_two_elements(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 2)

    def test_navbar_shows_my_basic_services_as_parent_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(items[0].text, self.translator.gettext("My basic services"))
        self.assertEqual(items[0].url, self.url_index.get_my_basic_services_url())

    def test_navbar_shows_create_basic_service_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(items[1].text, self.translator.gettext("Create basic service"))
        self.assertIsNone(items[1].url)
