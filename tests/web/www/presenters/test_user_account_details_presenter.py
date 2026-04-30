from datetime import datetime
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.datetime_service import datetime_min_utc, datetime_utc
from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors import get_user_account_details as interactor
from workers_control.web.www.presenters import (
    user_account_details_presenter as presenter,
)


class UserAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(presenter.UserAccountDetailsPresenter)

    def test_that_user_id_is_rendered_into_string_representation_of_itself(
        self,
    ) -> None:
        user_id = uuid4()
        response = self.create_response_with_user_info(user_id=user_id)
        view_model = self.presenter.render_user_account_details(response)
        assert view_model.user_id == str(user_id)

    def test_that_user_name_is_rendered_into_string_representation_of_itself(
        self,
    ) -> None:
        expected_user_name = "Test User"
        response = self.create_response_with_user_info(name=expected_user_name)
        view_model = self.presenter.render_user_account_details(response)
        assert view_model.user_name == expected_user_name

    def test_that_user_email_address_is_rendered_as_is(self) -> None:
        expected_email_address = "test@test.test"
        response = self.create_response_with_user_info(
            email_address=expected_email_address
        )
        view_model = self.presenter.render_user_account_details(response)
        assert view_model.email_address == expected_email_address

    def test_that_request_email_address_change_url_is_shown(self) -> None:
        response = self.create_response_with_user_info()
        view_model = self.presenter.render_user_account_details(response)
        assert (
            view_model.request_email_address_change_url
            == self.url_index.get_request_change_email_url()
        )

    def test_that_date_and_time_is_formatted_correctly(self) -> None:
        expected_time = datetime_utc(2025, 1, 1, 10, 20, 10)
        self.datetime_service.freeze_time(expected_time)
        response = self.create_response_with_user_info(current_time=expected_time)
        view_model = self.presenter.render_user_account_details(response)
        assert view_model.current_user_time.startswith("2025-01-01 10:20:10")

    @parameterized.expand(
        [
            (
                "Etc/GMT+3",
                " -0300 (-03)",
            ),
            ("UTC", " +0000 (UTC)"),
            ("Asia/Tokyo", " +0900 (JST)"),
        ]
    )
    def test_that_user_timezone_is_shown_correctly_based_on_timezone_configuration(
        self, configured_user_tz: str, expected_displayed_user_timezone: str
    ) -> None:
        self.timezone_configuration.set_timezone_of_current_user(configured_user_tz)
        expected_time = datetime_utc(2025, 1, 1, 10, 20, 10)
        self.datetime_service.freeze_time(expected_time)
        response = self.create_response_with_user_info(current_time=expected_time)
        view_model = self.presenter.render_user_account_details(response)
        assert view_model.current_user_time.endswith(expected_displayed_user_timezone)

    def create_response_with_user_info(
        self,
        user_id: UUID = uuid4(),
        email_address: str = "test@test.test",
        name: str = "Test User",
        current_time: datetime = datetime_min_utc(),
    ) -> interactor.Response:
        return interactor.Response(
            user_info=interactor.UserInfo(
                id=user_id,
                current_time=current_time,
                email_address=email_address,
                name=name,
            )
        )
