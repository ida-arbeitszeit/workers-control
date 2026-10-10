from parameterized import parameterized

from tests.flask_integration.base_test_case import ViewTestCase

PLOT_URL = "/plots/global_barplot_for_plans?productive_plans=1&public_plans=2"


class AnonymousUserTests(ViewTestCase):
    @parameterized.expand(
        [
            ("GET", "/logout"),
            ("GET", PLOT_URL),
            ("GET", "/unconfirmed-member"),
            ("POST", "/member/resend"),
        ]
    )
    def test_anonymous_user_gets_redirected_to_start_page(
        self, method: str, url: str
    ) -> None:
        response = self.client.open(url, method=method)
        assert response.status_code == 302
        assert response.location == "/"

    def test_anonymous_user_is_asked_to_log_in(self) -> None:
        response = self.client.get("/logout", follow_redirects=True)
        assert "Please log in to view this page." in response.text

    def test_user_is_not_logged_out_again_after_logging_in(self) -> None:
        self.client.get("/logout")
        self.login_member()
        response = self.client.get("/member/dashboard")
        assert response.status_code == 200


class AuthenticatedUserTests(ViewTestCase):
    def test_authenticated_user_gets_plot(self) -> None:
        self.login_member()
        response = self.client.get(PLOT_URL)
        assert response.status_code == 200
        assert response.mimetype == "image/png"
