from uuid import UUID, uuid4

from tests.datetime_service import datetime_utc
from workers_control.core.interactors import deactivate_basic_service
from workers_control.core.interactors.list_basic_services_of_worker import (
    ListBasicServicesOfWorkerInteractor,
)
from workers_control.core.interactors.list_basic_services_of_worker import (
    Request as ListRequest,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            deactivate_basic_service.DeactivateBasicServiceInteractor
        )

    def test_unknown_service_is_rejected_with_service_not_found(self) -> None:
        response = self.interactor.execute(
            deactivate_basic_service.Request(basic_service=uuid4())
        )
        assert (
            response.rejection_reason
            == deactivate_basic_service.RejectionReason.service_not_found
        )

    def test_active_service_is_deactivated_successfully(self) -> None:
        service_id = self.basic_service_generator.create_basic_service()
        response = self.interactor.execute(
            deactivate_basic_service.Request(basic_service=service_id)
        )
        assert not response.is_rejected
        assert response.rejection_reason is None

    def test_deactivation_sets_deactivated_on_to_current_datetime(self) -> None:
        expected_time = datetime_utc(2026, 5, 3, 9, 30)
        self.datetime_service.freeze_time(expected_time)
        service_id = self.basic_service_generator.create_basic_service()
        self.interactor.execute(
            deactivate_basic_service.Request(basic_service=service_id)
        )
        service = self.database_gateway.get_basic_services().with_id(service_id).first()
        assert service is not None
        assert service.deactivated_on == expected_time

    def test_already_deactivated_service_is_rejected(self) -> None:
        service_id = self.basic_service_generator.create_basic_service(deactivated=True)
        response = self.interactor.execute(
            deactivate_basic_service.Request(basic_service=service_id)
        )
        assert (
            response.rejection_reason
            == deactivate_basic_service.RejectionReason.already_deactivated
        )

    def test_deactivated_service_disappears_from_workers_list(self) -> None:
        member = self.member_generator.create_member()
        service_id = self.basic_service_generator.create_basic_service(member=member)
        assert self.service_is_on_worker_list(member, service_id)
        self.interactor.execute(
            deactivate_basic_service.Request(basic_service=service_id)
        )
        assert not self.service_is_on_worker_list(member, service_id)

    def service_is_on_worker_list(self, member: UUID, service_id: UUID) -> bool:
        list_interactor = self.injector.get(ListBasicServicesOfWorkerInteractor)
        response = list_interactor.list_basic_services_of_worker(
            ListRequest(member=member)
        )
        return service_id in [service.id for service in response.basic_services]
