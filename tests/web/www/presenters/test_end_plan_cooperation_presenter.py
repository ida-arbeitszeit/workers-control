from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.end_cooperation import EndCooperationResponse
from workers_control.web.www.presenters.end_plan_cooperation_presenter import (
    EndPlanCooperationPresenter,
)


class EndPlanCooperationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(EndPlanCooperationPresenter)

    def test_successful_response_shows_info_notification(self) -> None:
        self.presenter.render_response(EndCooperationResponse(rejection_reason=None))
        assert not self.notifier.warnings
        assert self.notifier.infos == [
            self.translator.gettext("Cooperation has been terminated.")
        ]

    def test_rejected_response_shows_warning_notification(self) -> None:
        self.presenter.render_response(
            EndCooperationResponse(
                rejection_reason=EndCooperationResponse.RejectionReason.plan_not_found
            )
        )
        assert not self.notifier.infos
        assert self.notifier.warnings == [
            self.translator.gettext("Cooperation could not be terminated.")
        ]

    @parameterized.expand(
        [(reason,) for reason in EndCooperationResponse.RejectionReason] + [(None,)]
    )
    def test_user_gets_redirected_to_my_cooperations_view(
        self, rejection_reason: EndCooperationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            EndCooperationResponse(rejection_reason=rejection_reason)
        )
        assert response.redirection_url == self.url_index.get_my_cooperations_url()
