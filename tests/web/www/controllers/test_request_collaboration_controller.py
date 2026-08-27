from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationRequest,
)
from workers_control.web.malformed_input_data import MalformedInputData
from workers_control.web.www.controllers.request_collaboration_controller import (
    RequestCollaborationController,
)


@dataclass
class FakeRequestCollaborationForm:
    plan_id: str
    collaboration_id: str

    def get_plan_id_string(self) -> str:
        return self.plan_id

    def get_collaboration_id_string(self) -> str:
        return self.collaboration_id


fake_form = FakeRequestCollaborationForm(
    plan_id=str(uuid4()), collaboration_id=str(uuid4())
)


class RequestCollaborationControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestCollaborationController)

    def test_when_user_is_not_authenticated_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        self.session.logout()
        self.assertIsNone(self.controller.import_form_data(form=fake_form))

    def test_when_user_is_authenticated_then_the_user_is_identified_in_interactor_request(
        self,
    ) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        interactor_request = self.controller.import_form_data(form=fake_form)
        assert interactor_request is not None
        assert isinstance(interactor_request, RequestCollaborationRequest)
        self.assertEqual(interactor_request.requester_id, expected_user_id)

    def test_returns_malformed_data_instance_if_plan_id_cannot_be_converted_to_uuid(
        self,
    ) -> None:
        malformed_form = replace(fake_form, plan_id="malformed plan id")
        self.session.login_company(uuid4())
        interactor_request = self.controller.import_form_data(form=malformed_form)
        assert interactor_request is not None
        assert isinstance(interactor_request, MalformedInputData)
        self.assertEqual(interactor_request.field, "plan_id")
        self.assertEqual(
            interactor_request.message, self.translator.gettext("Invalid plan ID.")
        )

    def test_returns_malformed_data_instance_if_collab_id_cannot_be_converted_to_uuid(
        self,
    ) -> None:
        malformed_form = replace(fake_form, collaboration_id="malformed collab id")
        self.session.login_company(uuid4())
        interactor_request = self.controller.import_form_data(form=malformed_form)
        assert interactor_request is not None
        assert isinstance(interactor_request, MalformedInputData)
        self.assertEqual(interactor_request.field, "collaboration_id")
        self.assertEqual(
            interactor_request.message,
            self.translator.gettext("Invalid collaboration ID."),
        )

    def test_controller_can_convert_plan_and_collaboration_id_into_correct_uuid(
        self,
    ) -> None:
        self.session.login_company(uuid4())
        interactor_request = self.controller.import_form_data(form=fake_form)
        assert interactor_request is not None
        assert isinstance(interactor_request, RequestCollaborationRequest)
        self.assertEqual(interactor_request.plan_id, UUID(fake_form.plan_id))
        self.assertEqual(
            interactor_request.collaboration_id, UUID(fake_form.collaboration_id)
        )
