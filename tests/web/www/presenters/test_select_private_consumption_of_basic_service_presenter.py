from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors import select_private_consumption_of_basic_service
from workers_control.web.www.presenters.select_private_consumption_of_basic_service_presenter import (
    SelectPrivateConsumptionOfBasicServicePresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(
            SelectPrivateConsumptionOfBasicServicePresenter
        )

    @parameterized.expand([(None,), (Decimal("0.5"),), (Decimal("10"),)])
    def test_no_basic_service_response_gets_rendered_correctly(
        self, amount: Decimal | None
    ) -> None:
        response = select_private_consumption_of_basic_service.NoBasicServiceResponse(
            amount=amount
        )
        view_model = self.presenter.render_response(response)
        assert view_model.valid_basic_service_selected is False
        assert view_model.basic_service_id is None
        assert view_model.basic_service_name is None
        assert view_model.basic_service_description is None
        assert view_model.provider_name is None
        assert view_model.amount == amount
        assert view_model.status_code == 200

    def test_no_warning_is_displayed_for_no_basic_service_response(self) -> None:
        assert not self.notifier.warnings
        response = select_private_consumption_of_basic_service.NoBasicServiceResponse(
            amount=None
        )
        self.presenter.render_response(response)
        assert not self.notifier.warnings

    def test_warning_is_displayed_when_basic_service_is_invalid(self) -> None:
        assert not self.notifier.warnings
        response = (
            select_private_consumption_of_basic_service.InvalidBasicServiceResponse(
                amount=Decimal("1")
            )
        )
        self.presenter.render_response(response)
        assert self.notifier.warnings

    @parameterized.expand([(None,), (Decimal("0.5"),), (Decimal("10"),)])
    def test_invalid_basic_service_response_gets_rendered_correctly(
        self, amount: Decimal | None
    ) -> None:
        response = (
            select_private_consumption_of_basic_service.InvalidBasicServiceResponse(
                amount=amount
            )
        )
        view_model = self.presenter.render_response(response)
        assert view_model.valid_basic_service_selected is False
        assert view_model.basic_service_id is None
        assert view_model.basic_service_name is None
        assert view_model.basic_service_description is None
        assert view_model.provider_name is None
        assert view_model.amount == amount
        assert view_model.status_code == 404

    @parameterized.expand(
        [
            (uuid4(), Decimal("1"), "BS Name", "BS Description", "Anna"),
            (uuid4(), Decimal("1.5"), "Yoga", "Mornings", "Ben"),
            (uuid4(), None, "BS", "Desc", "Provider"),
        ]
    )
    def test_valid_basic_service_response_gets_rendered_correctly(
        self,
        basic_service_id: UUID,
        amount: Decimal | None,
        basic_service_name: str,
        basic_service_description: str,
        provider_name: str,
    ) -> None:
        response = (
            select_private_consumption_of_basic_service.ValidBasicServiceResponse(
                basic_service_id=basic_service_id,
                amount=amount,
                basic_service_name=basic_service_name,
                basic_service_description=basic_service_description,
                provider_name=provider_name,
            )
        )
        view_model = self.presenter.render_response(response)
        assert view_model.valid_basic_service_selected is True
        assert view_model.basic_service_id == str(basic_service_id)
        assert view_model.basic_service_name == basic_service_name
        assert view_model.basic_service_description == basic_service_description
        assert view_model.provider_name == provider_name
        assert view_model.amount == amount
        assert view_model.status_code == 200
