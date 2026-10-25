from urllib.parse import urlparse

from flask import Flask, Response, abort, redirect, request
from werkzeug.wrappers import Response as WerkzeugResponse

CONTENT_SECURITY_POLICY = "default-src 'self'; frame-ancestors 'self'"
ONE_YEAR_IN_SECONDS = 365 * 24 * 60 * 60
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def initialize_http_security(app: Flask) -> None:
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.before_request(_reject_cross_origin_request)
    app.after_request(_set_security_headers)
    if app.config["FORCE_HTTPS"]:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.before_request(_redirect_to_https)
        app.after_request(_set_strict_transport_security_header)


def _reject_cross_origin_request() -> None:
    if request.method not in SAFE_METHODS and _is_cross_origin_request():
        abort(403, "Cross-origin request rejected.")


def _is_cross_origin_request() -> bool:
    fetch_site = request.headers.get("Sec-Fetch-Site")
    if fetch_site is not None:
        return fetch_site not in ("same-origin", "none")
    # Browsers send Sec-Fetch-Site only to HTTPS and localhost URLs, but
    # Origin over plain HTTP too.  A request with neither header does not
    # come from a current browser.
    origin = request.headers.get("Origin")
    return origin is not None and urlparse(origin).netloc != request.host


def _is_https() -> bool:
    return request.is_secure or request.headers.get("X-Forwarded-Proto") == "https"


def _redirect_to_https() -> WerkzeugResponse | None:
    if _is_https():
        return None
    return redirect(request.url.replace("http://", "https://", 1))


def _set_security_headers(response: Response) -> Response:
    response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "browsing-topics=()"
    return response


def _set_strict_transport_security_header(response: Response) -> Response:
    if _is_https():
        response.headers["Strict-Transport-Security"] = (
            f"max-age={ONE_YEAR_IN_SECONDS}; includeSubDomains"
        )
    return response
