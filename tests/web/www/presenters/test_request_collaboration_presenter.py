from typing import Optional

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationResponse,
)
from workers_control.web.www.presenters.request_collaboration_presenter import (
    RequestCollaborationPresenter,
)

RejectionReason = RequestCollaborationResponse.RejectionReason


class RequestCollaborationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestCollaborationPresenter)

    def test_that_a_redirect_url_is_returned_if_request_was_successful(self) -> None:
        view_model = self.presenter.present(self.get_successful_request())
        assert view_model.redirect_url is not None

    def test_that_redirect_leads_to_my_collaborations_page(self) -> None:
        view_model = self.presenter.present(self.get_successful_request())
        assert view_model.redirect_url == self.url_index.get_my_collaborations_url()

    def test_do_not_show_error_notificiation_if_request_was_successful(self) -> None:
        view_model = self.presenter.present(self.get_successful_request())
        assert view_model.error_notification is None

    def test_show_info_notification_if_request_was_successful(self) -> None:
        self.presenter.present(self.get_successful_request())
        assert len(self.notifier.infos) == 1
        assert self.notifier.infos[0] == self.translator.gettext(
            "Request has been sent."
        )
        assert not self.notifier.warnings

    def test_that_no_mail_was_sent_after_successful_request(self) -> None:
        self.presenter.present(self.get_successful_request())
        assert not self.email_service.sent_mails

    def test_no_redirect_url_is_returned_if_request_was_rejected(self) -> None:
        view_model = self.presenter.present(
            self.get_rejected_request(rejection_reason=RejectionReason.plan_not_found)
        )
        assert view_model.redirect_url is None

    def test_correct_notification_when_rejected_because_plan_not_found(self) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertEqual(
            presentation.error_notification, self.translator.gettext("Plan not found.")
        )

    def test_correct_notification_when_rejected_because_collab_not_found(self) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=RejectionReason.collaboration_not_found
            )
        )
        self.assertEqual(
            presentation.error_notification,
            self.translator.gettext("Collaboration not found."),
        )

    def test_correct_notification_when_rejected_because_plan_inactive(self) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertEqual(
            presentation.error_notification, self.translator.gettext("Plan not active.")
        )

    def test_correct_notification_when_rejected_because_plan_has_collaboration(
        self,
    ) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=RejectionReason.plan_has_collaboration
            )
        )
        self.assertEqual(
            presentation.error_notification,
            self.translator.gettext(
                "Plan is already collaborating or requested a collaboration."
            ),
        )

    def test_correct_notification_when_rejected_because_plan_is_requesting_collaboration(
        self,
    ) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=RejectionReason.plan_is_already_requesting_collaboration
            )
        )
        self.assertEqual(
            presentation.error_notification,
            self.translator.gettext(
                "Plan is already collaborating or requested a collaboration."
            ),
        )

    def test_correct_notification_when_rejected_because_plan_is_public_service(
        self,
    ) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=RejectionReason.plan_is_public_service
            )
        )
        self.assertEqual(
            presentation.error_notification,
            self.translator.gettext("Public plans cannot collaborate."),
        )

    def test_correct_notification_when_rejected_because_requester_not_planner(
        self,
    ) -> None:
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=RejectionReason.requester_is_not_planner
            )
        )
        self.assertEqual(
            presentation.error_notification,
            self.translator.gettext(
                "Only the creator of a plan can request a collaboration."
            ),
        )

    def get_rejected_request(
        self, rejection_reason: RequestCollaborationResponse.RejectionReason
    ) -> RequestCollaborationResponse:
        return RequestCollaborationResponse(
            coordinator_name=None,
            coordinator_email=None,
            rejection_reason=rejection_reason,
        )

    def get_successful_request(
        self,
        coordinator_mail: Optional[str] = None,
        coordinator_name: Optional[str] = None,
    ) -> RequestCollaborationResponse:
        if coordinator_mail is None:
            coordinator_mail = "company@comp.any"
        if coordinator_name is None:
            coordinator_name = "company xy"
        return RequestCollaborationResponse(
            coordinator_name=coordinator_name,
            coordinator_email=coordinator_mail,
            rejection_reason=None,
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestCollaborationPresenter)
        self.items = self.presenter.create_navbar_items()

    def test_navbar_shows_two_items(self) -> None:
        self.assertEqual(len(self.items), 2)

    def test_navbar_shows_my_collaborations_as_parent_page(self) -> None:
        assert self.items[0].text == self.translator.gettext("My collaborations")
        assert self.items[0].url == self.url_index.get_my_collaborations_url()

    def test_navbar_shows_request_collaboration_as_last_page(self) -> None:
        assert self.items[1].text == self.translator.gettext("Request collaboration")
        assert self.items[1].url is None
