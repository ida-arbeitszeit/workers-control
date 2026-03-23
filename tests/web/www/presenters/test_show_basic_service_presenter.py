from datetime import datetime

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.show_basic_service import (
    ShowBasicServiceResponse,
)
from workers_control.web.www.presenters.show_basic_service_presenter import (
    ShowBasicServicePresenter,
)


class ShowBasicServicePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowBasicServicePresenter)

    def test_returns_none_when_details_are_missing(self) -> None:
        response = ShowBasicServiceResponse(details=None)
        view_model = self.presenter.present(response)
        assert view_model is None

    def test_returns_view_model_when_details_are_present(self) -> None:
        response = self._create_response()
        view_model = self.presenter.present(response)
        assert view_model is not None

    def test_view_model_contains_correct_provider_name(self) -> None:
        expected_name = "Alice Smith"
        response = self._create_response(provider_name=expected_name)
        view_model = self.presenter.present(response)
        assert view_model is not None
        assert view_model.provider_name == expected_name

    def test_view_model_contains_correct_name(self) -> None:
        expected_name = "Haircut"
        response = self._create_response(name=expected_name)
        view_model = self.presenter.present(response)
        assert view_model is not None
        assert view_model.name == expected_name

    def test_view_model_contains_correct_description(self) -> None:
        expected_description = "Professional haircut service"
        response = self._create_response(description=expected_description)
        view_model = self.presenter.present(response)
        assert view_model is not None
        assert view_model.description == expected_description

    def test_view_model_contains_formatted_created_on(self) -> None:
        created_on = datetime(2026, 3, 22, 12, 0)
        response = self._create_response(created_on=created_on)
        view_model = self.presenter.present(response)
        assert view_model is not None
        expected_formatted = self.datetime_formatter.format_datetime(
            date=created_on,
            fmt="%d.%m.%Y %H:%M",
        )
        assert view_model.created_on == expected_formatted

    def _create_response(
        self,
        provider_name: str = "Test Provider",
        name: str = "Test Service",
        description: str = "Test Description",
        created_on: datetime | None = None,
    ) -> ShowBasicServiceResponse:
        if created_on is None:
            created_on = datetime(2026, 1, 1, 0, 0)
        return ShowBasicServiceResponse(
            details=ShowBasicServiceResponse.Details(
                provider_name=provider_name,
                name=name,
                description=description,
                created_on=created_on,
            ),
        )
