from dataclasses import dataclass

from workers_control.core.interactors import change_user_name as interactor
from workers_control.web.forms import ChangeUserNameForm
from workers_control.web.session import Session


@dataclass
class ChangeUserNameController:
    session: Session

    def process_change_user_name_request(
        self, form: ChangeUserNameForm
    ) -> interactor.Request:
        current_user_id = self.session.get_current_user()
        assert current_user_id
        return interactor.Request(
            user_id=current_user_id,
            new_name=form.new_name_field.get_value().strip(),
            current_password=form.current_password_field.get_value(),
        )
