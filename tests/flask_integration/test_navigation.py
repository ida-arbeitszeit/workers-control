from tests.flask_integration.base_test_case import ViewTestCase


class NavigationTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/help"

    def test_logged_in_member_sees_own_name_in_navigation(self) -> None:
        email = self.email_generator.get_random_email()
        self.member_generator.create_member(
            email=email, name="Navbar Member", password="password123"
        )
        self.login_member(email=email)
        response = self.client.get(self.url)
        assert "Navbar Member" in response.text

    def test_logged_in_company_sees_own_name_in_navigation(self) -> None:
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(
            email=email, name="Navbar Company", password="password123"
        )
        self.login_company(email=email)
        response = self.client.get(self.url)
        assert "Navbar Company" in response.text

    def test_logged_in_accountant_sees_own_name_in_navigation(self) -> None:
        self.login_accountant(name="Navbar Accountant")
        response = self.client.get(self.url)
        assert "Navbar Accountant" in response.text

    def test_long_user_names_are_truncated_in_navigation(self) -> None:
        self.login_accountant(name="Navbar Accountant With A Long Name")
        response = self.client.get(self.url)
        assert "Navbar Accountant With A Long Name" not in response.text
        assert "Navbar Accountant..." in response.text
