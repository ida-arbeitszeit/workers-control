from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.deny_cooperation import DenyCooperationResponse
from workers_control.web.www.presenters.deny_cooperation_presenter import (
    DenyCooperationPresenter,
)

_reason = DenyCooperationResponse.RejectionReason


class DenyCooperationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(DenyCooperationPresenter)

    def test_successfull_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(DenyCooperationResponse(rejection_reason=None))
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been denied."
        )

    @parameterized.expand(
        [
            (_reason.plan_not_found, "Plan or cooperation not found."),
            (_reason.cooperation_not_found, "Plan or cooperation not found."),
            (
                _reason.cooperation_was_not_requested,
                "This cooperation request does not exist.",
            ),
            (
                _reason.requester_is_not_coordinator,
                "You are not coordinator of this cooperation.",
            ),
            # not handled explicitly by the presenter, falls back to the catchall
            (_reason.plan_is_inactive, "Could not deny cooperation"),
        ]
    )
    def test_correct_warning_is_displayed_on_rejection(
        self, rejection_reason: DenyCooperationResponse.RejectionReason, message: str
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(message)

    @parameterized.expand(
        [(reason,) for reason in DenyCooperationResponse.RejectionReason]
    )
    def test_no_info_is_displayed_on_rejection(
        self, rejection_reason: DenyCooperationResponse.RejectionReason
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert not self.notifier.infos

    @parameterized.expand(
        [(reason,) for reason in DenyCooperationResponse.RejectionReason] + [(None,)]
    )
    def test_that_user_gets_redirected_to_my_cooperations_view(
        self, rejection_reason: DenyCooperationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            self.create_response(rejection_reason)
        )
        assert response.redirection_url == self.url_index.get_my_cooperations_url()

    def create_response(
        self, rejection_reason: DenyCooperationResponse.RejectionReason | None
    ) -> DenyCooperationResponse:
        return DenyCooperationResponse(rejection_reason=rejection_reason)
