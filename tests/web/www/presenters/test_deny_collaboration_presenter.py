from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.deny_collaboration import (
    DenyCollaborationResponse,
)
from workers_control.web.www.presenters.deny_collaboration_presenter import (
    DenyCollaborationPresenter,
)

_reason = DenyCollaborationResponse.RejectionReason


class DenyCollaborationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(DenyCollaborationPresenter)

    def test_successfull_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(DenyCollaborationResponse(rejection_reason=None))
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Collaboration request has been denied."
        )

    @parameterized.expand(
        [
            (_reason.plan_not_found, "Plan or collaboration not found."),
            (_reason.collaboration_not_found, "Plan or collaboration not found."),
            (
                _reason.collaboration_was_not_requested,
                "This collaboration request does not exist.",
            ),
            (
                _reason.requester_is_not_coordinator,
                "You are not coordinator of this collaboration.",
            ),
            # not handled explicitly by the presenter, falls back to the catchall
            (_reason.plan_is_inactive, "Could not deny collaboration"),
        ]
    )
    def test_correct_warning_is_displayed_on_rejection(
        self, rejection_reason: DenyCollaborationResponse.RejectionReason, message: str
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(message)

    @parameterized.expand(
        [(reason,) for reason in DenyCollaborationResponse.RejectionReason]
    )
    def test_no_info_is_displayed_on_rejection(
        self, rejection_reason: DenyCollaborationResponse.RejectionReason
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert not self.notifier.infos

    @parameterized.expand(
        [(reason,) for reason in DenyCollaborationResponse.RejectionReason] + [(None,)]
    )
    def test_that_user_gets_redirected_to_my_collaborations_view(
        self, rejection_reason: DenyCollaborationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            self.create_response(rejection_reason)
        )
        assert response.redirection_url == self.url_index.get_my_collaborations_url()

    def create_response(
        self, rejection_reason: DenyCollaborationResponse.RejectionReason | None
    ) -> DenyCollaborationResponse:
        return DenyCollaborationResponse(rejection_reason=rejection_reason)
