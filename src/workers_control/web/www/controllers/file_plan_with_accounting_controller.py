from uuid import UUID

from workers_control.core.interactors.file_plan_with_accounting import (
    FilePlanWithAccounting,
)
from workers_control.web.session import Session


class FilePlanWithAccountingController:
    class InvalidRequest(Exception):
        pass

    def process_file_plan_with_accounting_request(
        self, draft_id: str, session: Session
    ) -> FilePlanWithAccounting.Request:
        current_user = session.get_current_user()
        if current_user is None:
            raise self.InvalidRequest()
        try:
            draft_uuid = UUID(draft_id)
        except ValueError:
            raise self.InvalidRequest()
        return FilePlanWithAccounting.Request(
            draft_id=draft_uuid, filing_company=current_user
        )
