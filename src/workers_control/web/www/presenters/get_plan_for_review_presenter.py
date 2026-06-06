from __future__ import annotations

from dataclasses import dataclass

from workers_control.core.interactors.get_plan_for_review import (
    GetPlanForReviewInteractor as Interactor,
)
from workers_control.web.session import UserRole
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class GetPlanForReviewPresenter:
    @dataclass
    class ViewModel:
        product_name: str
        plan_details_url: str
        review_form_action_url: str
        navbar_items: list[NavbarItem]

    url_index: UrlIndex
    translator: Translator

    def present(self, response: Interactor.Response) -> ViewModel:
        return self.ViewModel(
            product_name=response.product_name,
            plan_details_url=self.url_index.get_plan_details_url(
                user_role=UserRole.accountant, plan_id=response.plan_id
            ),
            review_form_action_url=self.url_index.get_plan_review_url(response.plan_id),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("List unreviewed plans"),
                    url=self.url_index.get_unreviewed_plans_list_view_url(),
                ),
                NavbarItem(
                    text=self.translator.gettext("Review plan"),
                    url=None,
                ),
            ],
        )
