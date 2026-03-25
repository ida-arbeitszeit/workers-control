from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.list_basic_services_of_worker import (
    ListedBasicService,
    Response,
)
from workers_control.web.www.presenters.list_basic_services_of_worker_presenter import (
    ListBasicServicesOfWorkerPresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListBasicServicesOfWorkerPresenter)

    def test_empty_services_means_not_visible(self) -> None:
        response = Response(basic_services=[])
        view_model = self.presenter.present(response)
        assert view_model.is_services_visible is False

    def test_non_empty_services_means_visible(self) -> None:
        response = self._create_response_with_one_service()
        view_model = self.presenter.present(response)
        assert view_model.is_services_visible is True

    def test_service_name_is_passed_through(self) -> None:
        expected_name = "Haircut"
        response = self._create_response_with_one_service(name=expected_name)
        view_model = self.presenter.present(response)
        assert view_model.services[0].name == expected_name

    def test_service_description_is_passed_through(self) -> None:
        expected_description = "Professional haircut service"
        response = self._create_response_with_one_service(
            description=expected_description
        )
        view_model = self.presenter.present(response)
        assert view_model.services[0].description == expected_description

    def test_service_id_is_formatted_as_string(self) -> None:
        expected_id = uuid4()
        response = self._create_response_with_one_service(service_id=expected_id)
        view_model = self.presenter.present(response)
        assert view_model.services[0].id == str(expected_id)

    def test_created_on_is_formatted_via_datetime_formatter(self) -> None:
        created_on = datetime(2026, 3, 22, 12, 0)
        response = self._create_response_with_one_service(created_on=created_on)
        view_model = self.presenter.present(response)
        expected_formatted = self.datetime_formatter.format_datetime(
            date=created_on,
            fmt="%d.%m.%Y %H:%M",
        )
        assert view_model.services[0].created_on == expected_formatted

    def _create_response_with_one_service(
        self,
        service_id: UUID | None = None,
        name: str = "Test Service",
        description: str = "Test Description",
        created_on: datetime | None = None,
    ) -> Response:
        if service_id is None:
            service_id = uuid4()
        if created_on is None:
            created_on = datetime(2026, 1, 1, 0, 0)
        return Response(
            basic_services=[
                ListedBasicService(
                    id=service_id,
                    name=name,
                    description=description,
                    created_on=created_on,
                )
            ]
        )
