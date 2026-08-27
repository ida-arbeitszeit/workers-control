from tests.flask_integration.base_test_case import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.collaboration = self.collaboration_generator.create_collaboration()
        self.login_company()

    def test_that_requesting_view_results_in_200_status_code(self) -> None:
        response = self.client.get(
            f"/user/collaboration_summary/{self.collaboration}/coordinators"
        )
        self.assertEqual(response.status_code, 200)


class MemberViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.collaboration = self.collaboration_generator.create_collaboration()
        self.login_member()

    def test_that_requesting_view_results_in_200_status_code(self) -> None:
        response = self.client.get(
            f"/user/collaboration_summary/{self.collaboration}/coordinators"
        )
        self.assertEqual(response.status_code, 200)


class AccountantViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.collaboration = self.collaboration_generator.create_collaboration()
        self.login_accountant()

    def test_that_requesting_view_results_in_200_status_code(self) -> None:
        response = self.client.get(
            f"/user/collaboration_summary/{self.collaboration}/coordinators"
        )
        self.assertEqual(response.status_code, 200)
