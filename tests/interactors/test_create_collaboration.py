from uuid import uuid4

from workers_control.core.interactors.create_collaboration import (
    CreateCollaborationInteractor,
    CreateCollaborationRequest,
    CreateCollaborationResponse,
)

from ..base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.create_collaboration = self.injector.get(CreateCollaborationInteractor)

    def test_creation_rejected_when_coordinator_does_not_exist(self) -> None:
        request = CreateCollaborationRequest(
            coordinator_id=uuid4(), name="test name", definition="some info"
        )
        response = self.create_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateCollaborationResponse.RejectionReason.coordinator_not_found
        )

    def test_creation_is_rejected_when_collab_name_exists_already(self) -> None:
        self.collaboration_generator.create_collaboration(name="existing name")
        coordinator = self.company_generator.create_company()
        request = CreateCollaborationRequest(
            coordinator_id=coordinator, name="existing name", definition="some info"
        )
        response = self.create_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateCollaborationResponse.RejectionReason.collaboration_with_name_exists
        )

    def test_creation_is_rejected_when_collab_name_exists_with_case_variation(
        self,
    ) -> None:
        self.collaboration_generator.create_collaboration(name="ExisTing NaMe")
        coordinator = self.company_generator.create_company()
        request = CreateCollaborationRequest(
            coordinator_id=coordinator, name="existing name", definition="some info"
        )
        response = self.create_collaboration.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateCollaborationResponse.RejectionReason.collaboration_with_name_exists
        )

    def test_creation_is_successfull(self) -> None:
        coordinator = self.company_generator.create_company()
        request = CreateCollaborationRequest(
            coordinator_id=coordinator, name="test name", definition="some info"
        )
        response = self.create_collaboration.execute(request)
        assert response
