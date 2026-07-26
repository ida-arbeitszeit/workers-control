from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.accept_cooperation import (
    AcceptCooperationResponse,
)
from workers_control.web.www.presenters.accept_cooperation_request_presenter import (
    AcceptCooperationRequestPresenter,
)

_reason = AcceptCooperationResponse.RejectionReason


class ShowMyCooperationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(AcceptCooperationRequestPresenter)

    def test_successfull_accept_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(AcceptCooperationResponse(rejection_reason=None))
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been accepted."
        )
        assert not self.notifier.warnings

    @parameterized.expand(
        [
            (_reason.plan_not_found, "Plan or cooperation not found."),
            (_reason.cooperation_not_found, "Plan or cooperation not found."),
            (_reason.plan_inactive, "Something's wrong with that plan."),
            (_reason.plan_has_cooperation, "Something's wrong with that plan."),
            (_reason.plan_is_public_service, "Something's wrong with that plan."),
            (
                _reason.cooperation_was_not_requested,
                "This cooperation request does not exist.",
            ),
            (
                _reason.requester_is_not_coordinator,
                "You are not coordinator of this cooperation.",
            ),
        ]
    )
    def test_correct_warning_is_displayed_on_rejection(
        self,
        rejection_reason: AcceptCooperationResponse.RejectionReason,
        message: str,
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(message)

    @parameterized.expand(
        [(reason,) for reason in AcceptCooperationResponse.RejectionReason]
    )
    def test_no_info_is_displayed_on_rejection(
        self, rejection_reason: AcceptCooperationResponse.RejectionReason
    ) -> None:
        self.presenter.render_response(self.create_response(rejection_reason))
        assert not self.notifier.infos

    @parameterized.expand(
        [(reason,) for reason in AcceptCooperationResponse.RejectionReason] + [(None,)]
    )
    def test_that_user_gets_redirected_to_my_cooperations_view(
        self, rejection_reason: AcceptCooperationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            self.create_response(rejection_reason)
        )
        assert response.redirection_url == self.url_index.get_my_cooperations_url()

    def create_response(
        self, rejection_reason: AcceptCooperationResponse.RejectionReason | None
    ) -> AcceptCooperationResponse:
        return AcceptCooperationResponse(rejection_reason=rejection_reason)
