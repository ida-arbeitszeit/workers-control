from __future__ import annotations

from dataclasses import dataclass

from workers_control.core.interactors.get_draft_details import DraftDetailsSuccess
from workers_control.web.forms import DraftForm
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class GetDraftDetailsPresenter:
    @dataclass
    class ViewModel:
        cancel_url: str
        form: DraftForm

    url_index: UrlIndex
    translator: Translator

    def present_draft_details(self, draft_data: DraftDetailsSuccess) -> ViewModel:
        form = DraftForm(
            product_name_value=draft_data.product_name,
            description_value=draft_data.description,
            timeframe_value=str(draft_data.timeframe),
            unit_of_distribution_value=draft_data.production_unit,
            amount_value=str(draft_data.amount),
            means_cost_value=str(round(draft_data.means_cost, 2)),
            resource_cost_value=str(round(draft_data.resources_cost, 2)),
            labour_cost_value=str(round(draft_data.labour_cost, 2)),
            is_public_plan_value="on" if draft_data.is_public_service else "",
        )
        return self.ViewModel(
            cancel_url=self.url_index.get_my_plans_url(),
            form=form,
        )

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("My plans"),
                url=self.url_index.get_my_plans_url(),
            ),
            NavbarItem(
                text=self.translator.gettext("Edit draft"),
                url=None,
            ),
        ]
