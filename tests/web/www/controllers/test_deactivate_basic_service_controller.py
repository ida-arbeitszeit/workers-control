from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors import deactivate_basic_service
from workers_control.web.www.controllers.deactivate_basic_service_controller import (
    DeactivateBasicServiceController,
    InvalidRequest,
)


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(DeactivateBasicServiceController)

    def test_unknown_basic_service_id_returns_404(self) -> None:
        self.session.login_member(uuid4())
        result = self.controller.process_request(uuid4())
        assert isinstance(result, InvalidRequest)
        assert result.status_code == 404

    def test_foreign_owned_basic_service_returns_404(self) -> None:
        owner = self.member_generator.create_member()
        service_id = self.basic_service_generator.create_basic_service(member=owner)
        self.session.login_member(uuid4())
        result = self.controller.process_request(service_id)
        assert isinstance(result, InvalidRequest)
        assert result.status_code == 404

    def test_own_active_service_builds_interactor_request(self) -> None:
        member = self.member_generator.create_member()
        service_id = self.basic_service_generator.create_basic_service(member=member)
        self.session.login_member(member)
        result = self.controller.process_request(service_id)
        assert isinstance(result, deactivate_basic_service.Request)
        assert result.basic_service == service_id

    def test_own_already_deactivated_service_still_builds_request(self) -> None:
        member = self.member_generator.create_member()
        service_id = self.basic_service_generator.create_basic_service(
            member=member, deactivated=True
        )
        self.session.login_member(member)
        result = self.controller.process_request(service_id)
        assert isinstance(result, deactivate_basic_service.Request)
        assert result.basic_service == service_id
