from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.accept_collaboration import (
    AcceptCollaborationResponse,
)
from workers_control.web.www.presenters.accept_collaboration_request_presenter import (
    AcceptCollaborationRequestPresenter,
)

_reason = AcceptCollaborationResponse.RejectionReason


class ShowMyCollaborationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(AcceptCollaborationRequestPresenter)

    def test_successfull_accept_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(
            AcceptCollaborationResponse(rejection_reason=None)
        )
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Collaboration request has been accepted."
        )
        assert not self.notifier.warnings

    @parameterized.expand(
        [
            (_reason.plan_not_found, "Plan or collaboration not found."),
            (_reason.collaboration_not_found, "Plan or collaboration not found."),
            (_reason.plan_inactive, "Something's wrong with that plan."),
            (_reason.plan_has_collaboration, "Something's wrong with that plan."),
            (_reason.plan_is_public_service, "Something's wrong with that plan."),
            (
                _reason.collaboration_was_not_requested,
                "This collaboration request does not exist.",
            ),
            (
                _reason.requester_is_not_coordinator,
                "You are not coordinator of this collaboration.",
            ),
        ]
    )
    def test_correct_warning_is_displayed_on_rejection(
        self,
        rejection_reason: AcceptCollaborationResponse.RejectionReason,
        message: str,
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(message)

    @parameterized.expand(
        [(reason,) for reason in AcceptCollaborationResponse.RejectionReason]
    )
    def test_no_info_is_displayed_on_rejection(
        self, rejection_reason: AcceptCollaborationResponse.RejectionReason
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert not self.notifier.infos

    @parameterized.expand(
        [(reason,) for reason in AcceptCollaborationResponse.RejectionReason]
        + [(None,)]
    )
    def test_that_user_gets_redirected_to_my_collaborations_view(
        self, rejection_reason: AcceptCollaborationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            self.create_response(rejection_reason)
        )
        assert response.redirection_url == self.url_index.get_my_collaborations_url()

    def create_response(
        self, rejection_reason: AcceptCollaborationResponse.RejectionReason | None
    ) -> AcceptCollaborationResponse:
        return AcceptCollaborationResponse(rejection_reason=rejection_reason)
