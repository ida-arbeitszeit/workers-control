from dataclasses import dataclass

from workers_control.core.interactors.create_plan_draft import (
    Request as InteractorRequest,
)
from workers_control.core.records import ProductionCosts
from workers_control.web.forms import DraftForm
from workers_control.web.notification import Notifier
from workers_control.web.request import Request as WebRequest
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.www.controllers.draft_form_validator import DraftFormValidator


@dataclass
class CreateDraftController:
    session: Session
    translator: Translator
    notifier: Notifier
    form_validator: DraftFormValidator

    def import_form_data(self, request: WebRequest) -> InteractorRequest | DraftForm:
        planner = self.session.get_current_user()
        assert planner
        validation_result = self.form_validator.validate(request)
        if isinstance(validation_result, DraftForm):
            self.notifier.display_warning(
                self.translator.gettext("Please correct the errors in the form.")
            )
            return validation_result
        return InteractorRequest(
            planner=planner,
            product_name=validation_result.product_name,
            description=validation_result.description,
            timeframe_in_days=validation_result.timeframe,
            production_unit=validation_result.production_unit,
            production_amount=validation_result.amount,
            costs=ProductionCosts(
                labour_cost=validation_result.labour_cost,
                means_cost=validation_result.means_cost,
                resource_cost=validation_result.resource_cost,
            ),
            is_public_service=validation_result.is_public_plan,
        )
