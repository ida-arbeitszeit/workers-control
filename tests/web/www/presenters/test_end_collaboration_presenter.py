from typing import List
from uuid import uuid4

from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.end_cooperation import EndCooperationResponse
from workers_control.web.www.presenters.end_collaboration_presenter import (
    EndCollaborationPresenter,
)

SUCCESSFUL_RESPONSE = EndCooperationResponse(rejection_reason=None)

REJECTED_RESPONSE_PLAN_NOT_FOUND = EndCooperationResponse(
    rejection_reason=EndCooperationResponse.RejectionReason.plan_not_found,
)

REJECTED_RESPONSE_COLLABORATION_NOT_FOUND = EndCooperationResponse(
    rejection_reason=EndCooperationResponse.RejectionReason.cooperation_not_found,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(EndCollaborationPresenter)
        self.session.login_company(company=uuid4())

    def test_404_and_empty_url_returned_when_interactor_response_returned_plan_not_found(
        self,
    ) -> None:
        request = FakeRequest()
        view_model = self.presenter.present(
            REJECTED_RESPONSE_PLAN_NOT_FOUND, web_request=request
        )
        self.assertTrue(view_model.show_404)
        self.assertFalse(view_model.redirect_url)

    def test_notification_returned_when_operation_was_rejected_because_plan_was_not_found(
        self,
    ) -> None:
        request = FakeRequest()
        self.presenter.present(REJECTED_RESPONSE_PLAN_NOT_FOUND, web_request=request)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_notification_is_returned_when_operation_was_rejected_because_plan_was_not_found(
        self,
    ) -> None:
        request = FakeRequest()
        self.presenter.present(REJECTED_RESPONSE_PLAN_NOT_FOUND, web_request=request)
        self.assertIn(
            self.translator.gettext("Collaboration could not be terminated."),
            self._get_warning_notifications(),
        )

    def test_url_gets_returned_when_interactor_response_is_successfull(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg("plan_id", str(uuid4()))
        request.set_arg("collaboration_id", str(uuid4()))
        view_model = self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertFalse(view_model.show_404)
        self.assertTrue(view_model.redirect_url)

    def test_collab_summary_url_gets_returned_as_default_when_no_referer_is_given(
        self,
    ) -> None:
        request = FakeRequest()
        collab_id = uuid4()
        request.set_arg("plan_id", str(uuid4()))
        request.set_arg("collaboration_id", str(collab_id))
        view_model = self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertFalse(view_model.show_404)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_collab_summary_url(collab_id=collab_id),
        )

    def test_correct_notification_is_returned_when_operation_was_successfull(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg("plan_id", str(uuid4()))
        request.set_arg("collaboration_id", str(uuid4()))
        self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertIn(
            self.translator.gettext("Collaboration has been terminated."),
            self._get_info_notifications(),
        )

    def _get_info_notifications(self) -> List[str]:
        return self.notifier.infos

    def _get_warning_notifications(self) -> List[str]:
        return self.notifier.warnings
