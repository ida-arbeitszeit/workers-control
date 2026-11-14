from uuid import uuid4

from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationRequest,
)
from workers_control.web.forms import RequestCollaborationForm
from workers_control.web.www.controllers.request_collaboration_controller import (
    RequestCollaborationController,
)


class RequestCollaborationControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestCollaborationController)

    def test_when_user_is_not_authenticated_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        self.session.logout()
        self.assertIsNone(self.controller.import_form_data(create_request()))

    def test_when_user_is_authenticated_then_the_user_is_identified_in_interactor_request(
        self,
    ) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        result = self.controller.import_form_data(create_request())
        assert isinstance(result, RequestCollaborationRequest)
        self.assertEqual(result.requester_id, expected_user_id)

    def test_controller_can_convert_plan_and_collaboration_id_into_correct_uuid(
        self,
    ) -> None:
        plan_id = uuid4()
        collaboration_id = uuid4()
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(
            create_request(plan_id=str(plan_id), collaboration_id=str(collaboration_id))
        )
        assert isinstance(result, RequestCollaborationRequest)
        self.assertEqual(result.plan_id, plan_id)
        self.assertEqual(result.collaboration_id, collaboration_id)

    def test_controller_can_convert_ids_with_whitespace_into_correct_uuids(
        self,
    ) -> None:
        plan_id = uuid4()
        collaboration_id = uuid4()
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(
            create_request(
                plan_id=f"  {plan_id}  ", collaboration_id=f"  {collaboration_id}  "
            )
        )
        assert isinstance(result, RequestCollaborationRequest)
        self.assertEqual(result.plan_id, plan_id)
        self.assertEqual(result.collaboration_id, collaboration_id)

    def test_returns_form_with_plan_id_error_if_plan_id_cannot_be_converted_to_uuid(
        self,
    ) -> None:
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(
            create_request(plan_id="malformed plan id")
        )
        assert isinstance(result, RequestCollaborationForm)
        self.assertEqual(
            result.plan_id_errors, [self.translator.gettext("Invalid plan ID.")]
        )
        self.assertFalse(result.collaboration_id_errors)

    def test_returns_form_with_collab_id_error_if_collab_id_cannot_be_converted_to_uuid(
        self,
    ) -> None:
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(
            create_request(collaboration_id="malformed collab id")
        )
        assert isinstance(result, RequestCollaborationForm)
        self.assertEqual(
            result.collaboration_id_errors,
            [self.translator.gettext("Invalid collaboration ID.")],
        )
        self.assertFalse(result.plan_id_errors)

    def test_returns_form_with_errors_on_both_fields_if_both_ids_are_malformed(
        self,
    ) -> None:
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(
            create_request(plan_id="malformed", collaboration_id="malformed")
        )
        assert isinstance(result, RequestCollaborationForm)
        self.assertTrue(result.plan_id_errors)
        self.assertTrue(result.collaboration_id_errors)

    def test_returns_form_with_errors_on_both_fields_if_form_data_is_missing(
        self,
    ) -> None:
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(FakeRequest())
        assert isinstance(result, RequestCollaborationForm)
        self.assertTrue(result.plan_id_errors)
        self.assertTrue(result.collaboration_id_errors)

    def test_returned_form_keeps_submitted_values(self) -> None:
        collaboration_id = str(uuid4())
        self.session.login_company(uuid4())
        result = self.controller.import_form_data(
            create_request(plan_id="malformed", collaboration_id=collaboration_id)
        )
        assert isinstance(result, RequestCollaborationForm)
        self.assertEqual(result.plan_id_value, "malformed")
        self.assertEqual(result.collaboration_id_value, collaboration_id)


def create_request(
    *,
    plan_id: str | None = None,
    collaboration_id: str | None = None,
) -> FakeRequest:
    request = FakeRequest()
    request.set_form("plan_id", plan_id or str(uuid4()))
    request.set_form("collaboration_id", collaboration_id or str(uuid4()))
    return request
