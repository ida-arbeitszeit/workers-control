from parameterized import parameterized

from tests.flask_integration.base_test_case import ViewTestCase
from tests.flask_integration.dependency_injection import FlaskTestConfiguration
from workers_control.core.injector import Binder, CallableProvider, Module

URL = "/health"
FORM_URL = "/login-member"


class HttpSecurityTestCase(ViewTestCase):
    force_https: bool

    def get_injection_modules(self) -> list[Module]:
        force_https = self.force_https

        class _Module(Module):
            def configure(self, binder: Binder) -> None:
                super().configure(binder)
                binder[FlaskTestConfiguration] = CallableProvider(
                    _Module.provide_flask_configuration
                )

            @staticmethod
            def provide_flask_configuration() -> FlaskTestConfiguration:
                configuration = FlaskTestConfiguration.default()
                configuration["FORCE_HTTPS"] = force_https
                return configuration

        modules = super().get_injection_modules()
        modules.append(_Module())
        return modules

    def own_origin(self, scheme: str) -> str:
        return f"{scheme}://{self.app.config['SERVER_NAME']}"


class ForceHttpsTests(HttpSecurityTestCase):
    force_https = True

    def test_http_request_is_redirected_to_https(self) -> None:
        response = self.client.get(URL)
        assert response.status_code == 302
        assert response.location == self.own_origin("https") + URL

    def test_query_string_is_kept_when_redirecting_to_https(self) -> None:
        response = self.client.get(URL, query_string={"a": "b"})
        assert response.location == self.own_origin("https") + URL + "?a=b"

    def test_https_request_is_not_redirected(self) -> None:
        response = self.client.get(URL, base_url=self.own_origin("https"))
        assert response.status_code == 200

    def test_request_forwarded_from_https_proxy_is_not_redirected(self) -> None:
        response = self.client.get(URL, headers={"X-Forwarded-Proto": "https"})
        assert response.status_code == 200

    def test_request_forwarded_from_http_proxy_is_redirected(self) -> None:
        response = self.client.get(URL, headers={"X-Forwarded-Proto": "http"})
        assert response.status_code == 302

    def test_hsts_header_is_set_on_https_request(self) -> None:
        response = self.client.get(URL, base_url=self.own_origin("https"))
        assert (
            response.headers["Strict-Transport-Security"]
            == "max-age=31536000; includeSubDomains"
        )

    def test_hsts_header_is_set_on_request_forwarded_from_https_proxy(
        self,
    ) -> None:
        response = self.client.get(URL, headers={"X-Forwarded-Proto": "https"})
        assert "Strict-Transport-Security" in response.headers

    def test_session_cookie_is_only_sent_over_https(self) -> None:
        assert self.app.config["SESSION_COOKIE_SECURE"] is True


class NoForceHttpsTests(HttpSecurityTestCase):
    force_https = False

    def test_http_request_is_not_redirected(self) -> None:
        response = self.client.get(URL)
        assert response.status_code == 200

    def test_no_hsts_header_on_https_request(self) -> None:
        response = self.client.get(URL, base_url=self.own_origin("https"))
        assert "Strict-Transport-Security" not in response.headers

    def test_session_cookie_is_not_restricted_to_https(self) -> None:
        assert not self.app.config["SESSION_COOKIE_SECURE"]


class SecurityHeadersTests(HttpSecurityTestCase):
    force_https = False

    def test_content_security_policy_only_allows_own_origin(self) -> None:
        response = self.client.get(URL)
        assert (
            response.headers["Content-Security-Policy"]
            == "default-src 'self'; frame-ancestors 'self'"
        )

    def test_page_may_only_be_framed_by_own_origin(self) -> None:
        response = self.client.get(URL)
        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"

    def test_mime_type_sniffing_is_disabled(self) -> None:
        response = self.client.get(URL)
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_referrer_is_restricted_for_cross_origin_requests(self) -> None:
        response = self.client.get(URL)
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_topics_api_is_disabled(self) -> None:
        response = self.client.get(URL)
        assert response.headers["Permissions-Policy"] == "browsing-topics=()"


class SessionCookieTests(HttpSecurityTestCase):
    force_https = False

    def test_session_cookie_is_not_readable_by_javascript(self) -> None:
        assert self.app.config["SESSION_COOKIE_HTTPONLY"] is True

    def test_session_cookie_is_not_sent_with_cross_site_subrequests(self) -> None:
        assert self.app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


class CrossOriginRequestTests(HttpSecurityTestCase):
    force_https = False

    @parameterized.expand([("same-origin",), ("none",)])
    def test_post_reported_as_same_origin_or_user_initiated_is_allowed(
        self, fetch_site: str
    ) -> None:
        response = self.client.post(FORM_URL, headers={"Sec-Fetch-Site": fetch_site})
        assert response.status_code == 200

    @parameterized.expand([("same-site",), ("cross-site",)])
    def test_post_reported_as_cross_origin_is_rejected(self, fetch_site: str) -> None:
        response = self.client.post(FORM_URL, headers={"Sec-Fetch-Site": fetch_site})
        assert response.status_code == 403

    def test_sec_fetch_site_header_takes_precedence_over_origin_header(self) -> None:
        response = self.client.post(
            FORM_URL,
            headers={"Sec-Fetch-Site": "cross-site", "Origin": self.own_origin("http")},
        )
        assert response.status_code == 403

    def test_post_without_sec_fetch_site_from_own_origin_is_allowed(self) -> None:
        response = self.client.post(
            FORM_URL, headers={"Origin": self.own_origin("http")}
        )
        assert response.status_code == 200

    @parameterized.expand([("http://evil.example",), ("null",)])
    def test_post_without_sec_fetch_site_from_other_origin_is_rejected(
        self, origin: str
    ) -> None:
        response = self.client.post(FORM_URL, headers={"Origin": origin})
        assert response.status_code == 403

    def test_post_without_sec_fetch_site_and_origin_is_allowed(self) -> None:
        response = self.client.post(FORM_URL)
        assert response.status_code == 200

    def test_get_from_other_site_is_allowed(self) -> None:
        response = self.client.get(URL, headers={"Sec-Fetch-Site": "cross-site"})
        assert response.status_code == 200
