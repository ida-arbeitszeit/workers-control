from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors.request_coordination_transfer import (
    RequestCoordinationTransferInteractor as Interactor,
)
from workers_control.web.forms import RequestCoordinationTransferForm
from workers_control.web.forms.fields import parse_formfield
from workers_control.web.forms.formfield_parsers import UuidParser
from workers_control.web.session import Session


@dataclass
class RequestCoordinationTransferController:
    session: Session
    uuid_parser: UuidParser

    def import_form_data(
        self, form: RequestCoordinationTransferForm
    ) -> Optional[Interactor.Request]:
        candidate = parse_formfield(form.candidate_field(), self.uuid_parser)
        cooperation = parse_formfield(form.cooperation_field(), self.uuid_parser)
        current_user = self.session.get_current_user()
        if not (candidate and cooperation and current_user):
            return None
        return Interactor.Request(
            requester=current_user,
            cooperation=cooperation.value,
            candidate=candidate.value,
        )
