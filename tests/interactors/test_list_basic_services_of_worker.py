from uuid import uuid4

from tests.datetime_service import datetime_utc
from workers_control.core.interactors.list_basic_services_of_worker import (
    ListBasicServicesOfWorkerInteractor,
    Request,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListBasicServicesOfWorkerInteractor)

    def test_returns_empty_list_when_member_has_no_basic_services(self) -> None:
        member = self.member_generator.create_member()
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert response.basic_services == []

    def test_returns_empty_list_when_member_does_not_exist(self) -> None:
        response = self.interactor.list_basic_services_of_worker(
            Request(member=uuid4())
        )
        assert response.basic_services == []

    def test_returns_correct_number_of_services(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member)
        self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert len(response.basic_services) == 2

    def test_returns_correct_service_id(self) -> None:
        member = self.member_generator.create_member()
        expected_id = self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert response.basic_services[0].id == expected_id

    def test_returns_correct_service_name(self) -> None:
        member = self.member_generator.create_member()
        expected_name = "Haircut"
        self.basic_service_generator.create_basic_service(
            member=member, name=expected_name
        )
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert response.basic_services[0].name == expected_name

    def test_returns_correct_service_description(self) -> None:
        member = self.member_generator.create_member()
        expected_description = "Professional haircut service"
        self.basic_service_generator.create_basic_service(
            member=member, description=expected_description
        )
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert response.basic_services[0].description == expected_description

    def test_returns_correct_creation_timestamp(self) -> None:
        expected_time = datetime_utc(2026, 3, 22, 12, 0)
        self.datetime_service.freeze_time(expected_time)
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert response.basic_services[0].created_on == expected_time

    def test_does_not_include_services_of_another_member(self) -> None:
        member1 = self.member_generator.create_member()
        member2 = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member1)
        self.basic_service_generator.create_basic_service(member=member2)
        response = self.interactor.list_basic_services_of_worker(
            Request(member=member1)
        )
        assert len(response.basic_services) == 1

    def test_does_not_include_deactivated_services(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(
            member=member,
            deactivated=True,
        )
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert response.basic_services == []

    def test_includes_active_services_and_excludes_deactivated_services(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member)
        self.basic_service_generator.create_basic_service(
            member=member,
            deactivated=True,
        )
        response = self.interactor.list_basic_services_of_worker(Request(member=member))
        assert len(response.basic_services) == 1
