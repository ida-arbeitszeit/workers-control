from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors import select_private_consumption_of_basic_service


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            select_private_consumption_of_basic_service.SelectPrivateConsumptionOfBasicServiceInteractor
        )

    def test_no_basic_service_response_when_no_id_provided(self) -> None:
        response = self.interactor.select(self.create_request())
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.NoBasicServiceResponse,
        )

    def test_invalid_basic_service_response_when_id_does_not_exist(self) -> None:
        response = self.interactor.select(self.create_request(basic_service_id=uuid4()))
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.InvalidBasicServiceResponse,
        )

    def test_valid_basic_service_response_when_id_exists(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.interactor.select(self.create_request(basic_service_id=bs))
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.ValidBasicServiceResponse,
        )

    @parameterized.expand(
        [(None,), (Decimal("0"),), (Decimal("1.5"),), (Decimal("2"),)]
    )
    def test_amount_is_passed_to_response(self, amount: Decimal | None) -> None:
        response = self.interactor.select(self.create_request(amount=amount))
        assert response.amount == amount

    def test_basic_service_id_of_valid_response_matches_request(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.interactor.select(self.create_request(basic_service_id=bs))
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.ValidBasicServiceResponse,
        )
        assert response.basic_service_id == bs

    @parameterized.expand([("Yoga lessons",), ("Plumbing",)])
    def test_basic_service_name_is_returned(self, name: str) -> None:
        bs = self.basic_service_generator.create_basic_service(name=name)
        response = self.interactor.select(self.create_request(basic_service_id=bs))
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.ValidBasicServiceResponse,
        )
        assert response.basic_service_name == name

    @parameterized.expand([("Some description",), ("Another description",)])
    def test_basic_service_description_is_returned(self, description: str) -> None:
        bs = self.basic_service_generator.create_basic_service(description=description)
        response = self.interactor.select(self.create_request(basic_service_id=bs))
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.ValidBasicServiceResponse,
        )
        assert response.basic_service_description == description

    @parameterized.expand([("Anna",), ("Ben",)])
    def test_provider_name_is_returned(self, provider_name: str) -> None:
        provider = self.member_generator.create_member(name=provider_name)
        bs = self.basic_service_generator.create_basic_service(member=provider)
        response = self.interactor.select(self.create_request(basic_service_id=bs))
        assert isinstance(
            response,
            select_private_consumption_of_basic_service.ValidBasicServiceResponse,
        )
        assert response.provider_name == provider_name

    def create_request(
        self,
        basic_service_id: UUID | None = None,
        amount: Decimal | None = None,
    ) -> select_private_consumption_of_basic_service.Request:
        return select_private_consumption_of_basic_service.Request(
            basic_service_id=basic_service_id, amount=amount
        )
