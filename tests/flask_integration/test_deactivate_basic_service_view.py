from tests.flask_integration.base_test_case import ViewTestCase


class DeactivateTests(ViewTestCase):
    def _url(self, basic_service_id) -> str:
        return f"/member/basic_services/{basic_service_id}/deactivate"

    def test_post_with_own_service_redirects(self) -> None:
        member_id = self.login_member()
        service_id = self.basic_service_generator.create_basic_service(member=member_id)
        response = self.client.post(self._url(service_id))
        assert response.status_code == 302

    def test_post_with_own_service_deactivates_it_in_db(self) -> None:
        member_id = self.login_member()
        service_id = self.basic_service_generator.create_basic_service(member=member_id)
        self.client.post(self._url(service_id))
        service = self.database_gateway.get_basic_services().with_id(service_id).first()
        assert service is not None
        assert service.deactivated_on is not None
