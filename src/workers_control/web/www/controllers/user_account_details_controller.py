from dataclasses import dataclass

from workers_control.core.interactors import get_user_account_details as interactor
from workers_control.web.session import Session


@dataclass
class UserAccountDetailsController:
    session: Session

    def parse_web_request(self) -> interactor.Request:
        role = self.session.get_user_role()
        if role:
            user_id = self.session.get_current_user()
            assert user_id
            return interactor.Request(
                user_id=user_id,
            )
        else:
            raise Exception()
