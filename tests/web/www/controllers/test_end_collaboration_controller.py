from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.end_collaboration import EndCollaborationRequest
from workers_control.web.www.controllers.end_collaboration_controller import (
    EndCollaborationController,
)


class EndCollaborationControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(EndCollaborationController)

    def test_when_user_is_not_authenticated_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("collaboration_id", str(uuid4()))
        self.session.logout()
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_no_plan_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", "")
        request.set_form("collaboration_id", str(uuid4()))
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_a_malformed_plan_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", "jsbbjs8sjns")
        request.set_form("collaboration_id", str(uuid4()))
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_no_collaboration_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("collaboration_id", "")
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_malformed_collaboration_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("collaboration_id", "jnsjsn8snks")
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_a_interactor_request_can_get_returned(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("collaboration_id", str(uuid4()))
        self.session.login_company(uuid4())
        interactor_request = self.controller.process_request_data(request)
        self.assertIsNotNone(interactor_request)
        self.assertIsInstance(interactor_request, EndCollaborationRequest)

    def test_a_interactor_request_with_correct_attributes_gets_returned(
        self,
    ) -> None:
        request = FakeRequest()
        plan_id = str(uuid4())
        collaboration_id = str(uuid4())
        user_id = uuid4()
        request.set_form("plan_id", plan_id)
        request.set_form("collaboration_id", collaboration_id)
        self.session.login_company(user_id)
        interactor_request = self.controller.process_request_data(request)
        assert interactor_request
        self.assertEqual(interactor_request.plan_id, UUID(plan_id))
        self.assertEqual(interactor_request.collaboration_id, UUID(collaboration_id))
        self.assertEqual(interactor_request.requester_id, user_id)
