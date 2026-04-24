from dataclasses import dataclass

from workers_control.core.interactors.select_private_consumption import (
    InvalidPlanResponse,
    NoPlanResponse,
    ValidPlanResponse,
)
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator


@dataclass
class SelectPrivateConsumptionPresenter:
    notifier: Notifier
    translator: Translator

    @dataclass
    class ViewModel:
        valid_plan_selected: bool
        plan_id: str | None
        plan_name: str | None
        plan_description: str | None
        amount: int | None
        status_code: int

    def render_response(
        self, response: NoPlanResponse | InvalidPlanResponse | ValidPlanResponse
    ) -> ViewModel:
        if isinstance(response, NoPlanResponse):
            return self.ViewModel(
                valid_plan_selected=False,
                plan_id=None,
                plan_name=None,
                plan_description=None,
                amount=response.amount,
                status_code=200,
            )
        if isinstance(response, InvalidPlanResponse):
            self.notifier.display_warning(
                self.translator.gettext(
                    "The selected plan does not exist or is not active anymore."
                )
            )
            return self.ViewModel(
                valid_plan_selected=False,
                plan_id=None,
                plan_name=None,
                plan_description=None,
                amount=response.amount,
                status_code=404,
            )
        assert isinstance(response, ValidPlanResponse)
        return self.ViewModel(
            valid_plan_selected=True,
            plan_id=str(response.plan_id),
            plan_name=response.plan_name,
            plan_description=response.plan_description,
            amount=response.amount,
            status_code=200,
        )
