from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
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

    def test_delete_url_is_built_from_url_index(self) -> None:
        service_id = uuid4()
        response = self._create_response_with_one_service(service_id=service_id)
        view_model = self.presenter.present(response)
        expected_url = self.url_index.get_deactivate_basic_service_url(
            basic_service_id=service_id
        )
        assert view_model.services[0].delete_url == expected_url

    def test_each_service_has_its_own_delete_url(self) -> None:
        first_id = uuid4()
        second_id = uuid4()
        response = Response(
            basic_services=[
                ListedBasicService(
                    id=first_id,
                    name="A",
                    description="d",
                    created_on=datetime(2026, 1, 1, 0, 0),
                ),
                ListedBasicService(
                    id=second_id,
                    name="B",
                    description="d",
                    created_on=datetime(2026, 1, 1, 0, 0),
                ),
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.services[0].delete_url != view_model.services[1].delete_url

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


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListBasicServicesOfWorkerPresenter)

    def test_navbar_shows_my_basic_services_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].text, self.translator.gettext("My basic services"))
        self.assertIsNone(items[0].url)
