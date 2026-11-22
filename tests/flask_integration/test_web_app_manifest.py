import json
import struct
from typing import Any

from parameterized import parameterized

from tests.flask_integration.base_test_case import ViewTestCase

MANIFEST_URL = "/static/manifest.webmanifest"


def png_size(data: bytes) -> str:
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    width, height = struct.unpack(">II", data[16:24])
    return f"{width}x{height}"


class WebAppManifestTests(ViewTestCase):
    def test_that_manifest_is_served_with_manifest_media_type(self) -> None:
        response = self.client.get(MANIFEST_URL)
        assert response.status_code == 200
        assert response.mimetype == "application/manifest+json"

    def test_that_manifest_is_linked_in_base_template(self) -> None:
        response = self.client.get("/")
        assert (
            '<link rel="manifest" href="/static/manifest.webmanifest">' in response.text
        )

    def test_that_installed_app_starts_on_start_page(self) -> None:
        assert self.get_manifest()["start_url"] == "/"

    def test_that_installed_app_opens_in_standalone_window(self) -> None:
        assert self.get_manifest()["display"] == "standalone"

    @parameterized.expand(
        [
            ("192x192", "any"),
            ("512x512", "any"),
            ("512x512", "maskable"),
        ]
    )
    def test_that_manifest_declares_icon(self, sizes: str, purpose: str) -> None:
        icons = self.get_manifest()["icons"]
        assert any(
            icon["sizes"] == sizes and icon["purpose"] == purpose for icon in icons
        )

    def test_that_declared_icons_are_pngs_of_declared_size(self) -> None:
        for icon in self.get_manifest()["icons"]:
            response = self.client.get(f"/static/{icon['src']}")
            assert response.status_code == 200
            assert response.mimetype == icon["type"] == "image/png"
            assert png_size(response.data) == icon["sizes"]

    def get_manifest(self) -> dict[str, Any]:
        response = self.client.get(MANIFEST_URL)
        return json.loads(response.data)


class AppleTouchIconTests(ViewTestCase):
    def test_that_apple_touch_icon_is_a_png_of_180_pixels(self) -> None:
        response = self.client.get("/static/apple-touch-icon.png")
        assert response.status_code == 200
        assert png_size(response.data) == "180x180"

    def test_that_apple_touch_icon_is_linked_in_base_template(self) -> None:
        response = self.client.get("/")
        assert (
            '<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">'
            in response.text
        )
