from typing import Optional
from urllib.parse import urljoin, urlparse
from uuid import UUID

from flask import request, session

from workers_control.web.session import UserRole


def is_safe_url(target: str, host_url: str) -> bool:
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ("http", "https") and (
        test_url.netloc == "" or test_url.netloc == ref_url.netloc
    )


class FlaskSession:
    ROLES = {
        "member": UserRole.member,
        "company": UserRole.company,
        "accountant": UserRole.accountant,
    }

    def get_user_role(self) -> Optional[UserRole]:
        user_type = session.get("user_type")
        if user_type is None or self.get_current_user() is None:
            return None
        return self.ROLES.get(user_type)

    def is_logged_in_as_member(self) -> bool:
        return self.get_user_role() == UserRole.member

    def is_logged_in_as_company(self) -> bool:
        return self.get_user_role() == UserRole.company

    def is_logged_in_as_accountant(self) -> bool:
        return self.get_user_role() == UserRole.accountant

    def get_current_user(self) -> Optional[UUID]:
        return session.get("user_id")

    def is_current_user_authenticated(self) -> bool:
        return self.get_current_user() is not None

    def login_member(self, member: UUID, remember: bool = False) -> None:
        self._login(member, "member", remember)

    def login_company(self, company: UUID, remember: bool = False) -> None:
        self._login(company, "company", remember)

    def login_accountant(self, accountant: UUID, remember: bool = False) -> None:
        self._login(accountant, "accountant", remember)

    def _login(self, user_id: UUID, user_type: str, remember: bool) -> None:
        session["user_id"] = user_id
        session["user_type"] = user_type
        session.permanent = remember

    def logout(self) -> None:
        session.pop("user_id", None)
        session["user_type"] = None
        session.permanent = False

    def pop_next_url(self) -> Optional[str]:
        return session.pop("next", None)

    def set_next_url(self, next_url: str) -> None:
        if is_safe_url(next_url, request.base_url):
            session["next"] = next_url
