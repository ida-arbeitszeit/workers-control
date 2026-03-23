from uuid import UUID, uuid4

from tests.datetime_service import datetime_utc
from workers_control.core import records
from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceInteractor,
    CreateBasicServiceRequest,
    CreateBasicServiceResponse,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(CreateBasicServiceInteractor)

    def test_creation_rejected_when_member_does_not_exist(self) -> None:
        request = self.create_interactor_request(member_id=uuid4())
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateBasicServiceResponse.RejectionReason.member_not_found
        )

    def test_creation_is_successful(self) -> None:
        member = self.member_generator.create_member()
        request = self.create_interactor_request(member_id=member)
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert response.basic_service_id is not None

    def test_basic_service_id_is_none_when_rejected(self) -> None:
        request = self.create_interactor_request(member_id=uuid4())
        response = self.interactor.execute(request)
        assert response.basic_service_id is None

    def test_created_basic_service_is_stored_in_database(self) -> None:
        expected_name = "Haircut"
        expected_description = "Professional haircut service"
        member = self.member_generator.create_member()
        request = self.create_interactor_request(
            member_id=member, name=expected_name, description=expected_description
        )
        response = self.interactor.execute(request)
        assert response.basic_service_id is not None
        service = self.get_basic_service_from_database(response.basic_service_id)
        assert service is not None
        assert service.name == expected_name
        assert service.description == expected_description
        assert service.provider == member

    def test_created_basic_service_has_correct_provider(self) -> None:
        member = self.member_generator.create_member()
        request = self.create_interactor_request(member_id=member)
        response = self.interactor.execute(request)
        assert response.basic_service_id is not None
        service = self.get_basic_service_from_database(response.basic_service_id)
        assert service is not None
        assert service.provider == member

    def test_created_basic_service_has_correct_creation_timestamp(self) -> None:
        expected_time = datetime_utc(2026, 3, 22, 12, 0)
        self.datetime_service.freeze_time(expected_time)
        member = self.member_generator.create_member()
        request = self.create_interactor_request(member_id=member)
        response = self.interactor.execute(request)
        assert response.basic_service_id is not None
        service = self.get_basic_service_from_database(response.basic_service_id)
        assert service is not None
        assert service.created_on == expected_time

    def create_interactor_request(
        self,
        member_id: UUID | None = None,
        name: str = "Default Service Name",
        description: str = "Default Service Description",
    ) -> CreateBasicServiceRequest:
        if member_id is None:
            member_id = uuid4()
        return CreateBasicServiceRequest(
            member_id=member_id, name=name, description=description
        )

    def get_basic_service_from_database(
        self, basic_service_id: UUID
    ) -> records.BasicService:
        basic_service = (
            self.database_gateway.get_basic_services().with_id(basic_service_id).first()
        )
        assert basic_service is not None
        return basic_service
