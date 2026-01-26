from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.deny_cooperation import DenyCooperationResponse
from workers_control.web.www.presenters.deny_cooperation_presenter import (
    DenyCooperationPresenter,
)


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

    def test_failed_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(
            deny_cooperation_response=DenyCooperationResponse(
                rejection_reason=DenyCooperationResponse.RejectionReason.plan_not_found
            )
        )
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan or cooperation not found."
        )

    @parameterized.expand(
        [(reason,) for reason in DenyCooperationResponse.RejectionReason] + [(None,)]
    )
    def test_that_user_gets_redirected_to_my_cooperations_view(
        self, rejection_reason: DenyCooperationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            deny_cooperation_response=DenyCooperationResponse(
                rejection_reason=rejection_reason
            )
        )
        assert response.redirection_url == self.url_index.get_my_cooperations_url()
