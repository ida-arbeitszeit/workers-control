from dataclasses import dataclass
from typing import Protocol

from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceRequest,
)
from workers_control.web.session import Session


class CreateBasicServiceForm(Protocol):
    def get_name_string(self) -> str: ...

    def get_description_string(self) -> str: ...


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class CreateBasicServiceController:
    session: Session

    def import_form_data(
        self, form: CreateBasicServiceForm
    ) -> CreateBasicServiceRequest | InvalidRequest:
        user_id = self.session.get_current_user()
        if not user_id:
            return InvalidRequest(status_code=401)
        return CreateBasicServiceRequest(
            member_id=user_id,
            name=form.get_name_string(),
            description=form.get_description_string(),
        )
