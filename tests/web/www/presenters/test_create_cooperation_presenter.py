from typing import List
from uuid import uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.create_cooperation import (
    CreateCooperationResponse,
)
from workers_control.web.www.presenters.create_cooperation_presenter import (
    CreateCooperationPresenter,
)

SUCCESSFUL_CREATE_RESPONSE = CreateCooperationResponse(
    rejection_reason=None, cooperation_id=uuid4()
)

REJECTED_RESPONSE_NAME_EXISTS = CreateCooperationResponse(
    rejection_reason=CreateCooperationResponse.RejectionReason.cooperation_with_name_exists,
    cooperation_id=None,
)

REJECTED_RESPONSE_COORDINATOR_NOT_FOUND = CreateCooperationResponse(
    rejection_reason=CreateCooperationResponse.RejectionReason.coordinator_not_found,
    cooperation_id=None,
)


class CreateCooperationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateCooperationPresenter)

    def test_notification_returned_when_creation_was_successful(self) -> None:
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertTrue(self._get_info_notifications())

    def test_correct_notification_returned_when_creation_was_successful(self) -> None:
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertIn(
            self.translator.gettext("Successfully created cooperation."),
            self._get_info_notifications(),
        )

    def test_notification_returned_when_creation_was_rejected_because_coop_name_existed(
        self,
    ) -> None:
        self.presenter.present(REJECTED_RESPONSE_NAME_EXISTS)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_notification_is_returned_when_creation_was_rejected_because_coop_name_existed(
        self,
    ) -> None:
        self.presenter.present(REJECTED_RESPONSE_NAME_EXISTS)
        self.assertIn(
            self.translator.gettext(
                "There is already a cooperation with the same name."
            ),
            self._get_warning_notifications(),
        )

    def test_notification_returned_when_creation_was_rejected_because_coordinator_not_found(
        self,
    ) -> None:
        self.presenter.present(REJECTED_RESPONSE_COORDINATOR_NOT_FOUND)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_notification_is_returned_when_creation_was_rejected_because_coordinator_not_found(
        self,
    ) -> None:
        self.presenter.present(REJECTED_RESPONSE_COORDINATOR_NOT_FOUND)
        self.assertIn(
            self.translator.gettext("Internal error: Coordinator not found."),
            self._get_warning_notifications(),
        )

    def _get_info_notifications(self) -> List[str]:
        return self.notifier.infos

    def _get_warning_notifications(self) -> List[str]:
        return self.notifier.warnings


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateCooperationPresenter)

    def test_navbar_links_to_my_cooperations_then_shows_create_as_current_page(
        self,
    ) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].text, self.translator.gettext("My cooperations"))
        self.assertEqual(items[0].url, self.url_index.get_my_cooperations_url())
        self.assertEqual(items[1].text, self.translator.gettext("Create Cooperation"))
        self.assertIsNone(items[1].url)
