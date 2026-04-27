from decimal import Decimal
from uuid import uuid4

from .base_test_case import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()
        self.url = "/member/register_private_consumption_of_basic_service"

    def test_get_returns_200_status(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_with_invalid_basic_service_id_returns_error_status(self) -> None:
        response = self.client.get(f"{self.url}?basic_service_id=not_a_valid_uuid")
        assert response.status_code >= 400

    def test_get_with_unknown_basic_service_id_returns_404(self) -> None:
        response = self.client.get(f"{self.url}?basic_service_id={uuid4()}")
        self.assertEqual(response.status_code, 404)

    def test_get_without_basic_service_id_does_not_render_readonly_field(self) -> None:
        response = self.client.get(self.url)
        assert "readonly" not in response.text

    def test_get_with_valid_basic_service_id_renders_summary_in_html(self) -> None:
        provider = self.member_generator.create_member()
        expected_name = "Basic service 1234"
        expected_description = "Basic service description 1234"
        bs = self.basic_service_generator.create_basic_service(
            member=provider,
            name=expected_name,
            description=expected_description,
        )
        response = self.client.get(f"{self.url}?basic_service_id={bs}")
        self.assertEqual(response.status_code, 200)
        assert str(bs) in response.text
        assert expected_name in response.text
        assert expected_description in response.text

    def test_get_with_valid_basic_service_id_renders_readonly_field(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.client.get(f"{self.url}?basic_service_id={bs}")
        assert "readonly" in response.text

    def test_get_with_valid_basic_service_id_renders_cancel_button(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.client.get(f"{self.url}?basic_service_id={bs}")
        assert ">Cancel</a>" in response.text

    def test_posting_without_data_results_in_400(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_posting_with_invalid_form_data_results_in_400(self) -> None:
        response = self.client.post(
            self.url,
            data=dict(
                basic_service_id=uuid4(),
                amount="abc",
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_posting_with_valid_form_data_results_in_302(self) -> None:
        account = (
            self.database_gateway.get_accounts().owned_by_member(self.member).first()
        )
        assert account
        self.transfer_generator.create_transfer(
            credit_account=account.id,
            value=Decimal(100),
        )
        bs = self.basic_service_generator.create_basic_service()
        response = self.client.post(
            self.url,
            data=dict(
                basic_service_id=bs,
                amount=2,
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_posting_with_nonexisting_basic_service_id_results_in_404(self) -> None:
        response = self.client.post(
            self.url,
            data=dict(
                basic_service_id=uuid4(),
                amount=2,
            ),
        )
        self.assertEqual(response.status_code, 404)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()
        self.url = "/member/register_private_consumption_of_basic_service"

    def test_company_gets_redirected_when_trying_to_access_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
