from datetime import datetime
from uuid import uuid4

from tests.datetime_service import datetime_utc
from workers_control.core.interactors.show_basic_service import (
    ShowBasicServiceInteractor,
    ShowBasicServiceRequest,
    ShowBasicServiceResponse,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ShowBasicServiceInteractor)

    def test_returns_no_details_when_basic_service_does_not_exist(self) -> None:
        request = ShowBasicServiceRequest(basic_service_id=uuid4())
        response = self.interactor.show_basic_service(request)
        assert response.details is None

    def test_returns_details_when_basic_service_exists(self) -> None:
        member = self.member_generator.create_member()
        basic_service_id = self.basic_service_generator.create_basic_service(
            member=member,
        )
        request = ShowBasicServiceRequest(basic_service_id=basic_service_id)
        response = self.interactor.show_basic_service(request)
        assert response.details is not None

    def test_returns_correct_name(self) -> None:
        expected_name = "Haircut"
        response = self.create_and_show_basic_service(service_name=expected_name)
        assert response.details is not None
        assert response.details.name == expected_name

    def test_returns_correct_description(self) -> None:
        expected_description = "Professional haircut service"
        response = self.create_and_show_basic_service(description=expected_description)
        assert response.details is not None
        assert response.details.description == expected_description

    def test_returns_correct_provider_name(self) -> None:
        expected_name = "Alice Smith"
        response = self.create_and_show_basic_service(member_name=expected_name)
        assert response.details is not None
        assert response.details.provider_name == expected_name

    def test_returns_correct_creation_timestamp(self) -> None:
        expected_time = datetime_utc(1990, 1, 1, 12, 0)
        response = self.create_and_show_basic_service(created_on=expected_time)
        assert response.details is not None
        assert response.details.created_on == expected_time

    def create_and_show_basic_service(
        self,
        member_name: str = "Test Member",
        service_name: str = "Test Service",
        description: str = "Test Description",
        created_on: datetime = datetime_utc(2026, 3, 22, 12, 0),
    ) -> ShowBasicServiceResponse:
        self.datetime_service.freeze_time(created_on)
        member = self.member_generator.create_member(name=member_name)
        basic_service_id = self.basic_service_generator.create_basic_service(
            member=member, name=service_name, description=description
        )
        request = ShowBasicServiceRequest(basic_service_id=basic_service_id)
        return self.interactor.show_basic_service(request)
