from flask import Flask, Response, redirect, request
from werkzeug.wrappers import Response as WerkzeugResponse

CONTENT_SECURITY_POLICY = "default-src 'self'; frame-ancestors 'self'"
ONE_YEAR_IN_SECONDS = 365 * 24 * 60 * 60


def initialize_http_security(app: Flask) -> None:
    app.after_request(_set_security_headers)
    if app.config["DEBUG"]:
        return
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if app.config["FORCE_HTTPS"]:
        app.before_request(_redirect_to_https)
    app.after_request(_set_strict_transport_security_header)


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
