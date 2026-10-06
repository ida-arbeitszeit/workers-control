from tests.flask_integration.base_test_case import ViewTestCase


class FaviconTests(ViewTestCase):
    def test_that_getting_favicon_route_yields_200(self) -> None:
        response = self.client.get("/static/favicon.ico")
        assert response.status_code == 200

    def test_that_getting_svg_favicon_route_yields_200(self) -> None:
        response = self.client.get("/static/favicon.svg")
        assert response.status_code == 200

    def test_that_a_favicon_is_linked_in_base_template(self) -> None:
        response = self.client.get("/")
        assert (
            """<link rel="icon" href="/static/favicon.ico" sizes="32x32">"""
            in response.text
        )

    def test_that_an_svg_favicon_is_linked_in_base_template(self) -> None:
        response = self.client.get("/")
        assert (
            """<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">"""
            in response.text
        )
