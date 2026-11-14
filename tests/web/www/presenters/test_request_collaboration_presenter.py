from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationResponse,
)
from workers_control.web.forms import RequestCollaborationForm
from workers_control.web.www.presenters.request_collaboration_presenter import (
    RequestCollaborationPresenter,
)
from workers_control.web.www.response import Redirect

RejectionReason = RequestCollaborationResponse.RejectionReason


class RequestCollaborationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestCollaborationPresenter)

    def test_that_view_returns_a_redirect_object_if_request_was_successful(
        self,
    ) -> None:
        view_model = self.presenter.present(
            self.get_successful_request(), FakeRequest()
        )
        assert isinstance(view_model, Redirect)

    def test_that_redirect_leads_to_my_collaborations_page(self) -> None:
        view_model = self.presenter.present(
            self.get_successful_request(), FakeRequest()
        )
        assert isinstance(view_model, Redirect)
        assert view_model.url == self.url_index.get_my_collaborations_url()

    def test_show_that_info_notification_is_issued_if_request_was_successful(
        self,
    ) -> None:
        self.presenter.present(self.get_successful_request(), FakeRequest())
        assert not self.notifier.warnings
        assert len(self.notifier.infos) == 1
        assert self.notifier.infos[0] == self.translator.gettext(
            "Request has been sent."
        )

    def test_that_warning_notification_is_issued_if_request_was_rejected(self) -> None:
        self.presenter.present(self.get_rejected_request(), FakeRequest())
        assert not self.notifier.infos
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Request was not successful."
        )

    def test_form_is_returned_if_request_was_rejected(self) -> None:
        view_model = self.presenter.present(self.get_rejected_request(), FakeRequest())
        assert isinstance(view_model, RequestCollaborationForm)

    def test_that_form_is_returned_with_original_plan_and_collab_id(self) -> None:
        original_plan_id = str(uuid4())
        original_collab_id = str(uuid4())
        request = FakeRequest()
        request.set_form("plan_id", original_plan_id)
        request.set_form("collaboration_id", original_collab_id)
        view_model = self.presenter.present(self.get_rejected_request(), request)
        assert isinstance(view_model, RequestCollaborationForm)
        assert view_model.plan_id_value == original_plan_id
        assert view_model.collaboration_id_value == original_collab_id

    @parameterized.expand(
        [
            (RejectionReason.plan_not_found, "Plan not found."),
            (RejectionReason.collaboration_not_found, "Collaboration not found."),
            (RejectionReason.plan_inactive, "Plan not active."),
            (
                RejectionReason.plan_has_collaboration,
                "Plan is already collaborating or requested a collaboration.",
            ),
            (
                RejectionReason.plan_is_already_requesting_collaboration,
                "Plan is already collaborating or requested a collaboration.",
            ),
            (
                RejectionReason.plan_is_public_service,
                "Public plans cannot collaborate.",
            ),
            (
                RejectionReason.requester_is_not_planner,
                "Only the creator of a plan can request a collaboration.",
            ),
        ]
    )
    def test_the_correct_error_per_rejection_reason_is_appended_to_form(
        self, rejection_reason: RejectionReason, error_message: str
    ) -> None:
        view_model = self.presenter.present(
            self.get_rejected_request(rejection_reason=rejection_reason), FakeRequest()
        )
        assert isinstance(view_model, RequestCollaborationForm)
        assert view_model.general_errors == [self.translator.gettext(error_message)]

    def get_rejected_request(
        self, rejection_reason: RejectionReason = RejectionReason.plan_not_found
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
