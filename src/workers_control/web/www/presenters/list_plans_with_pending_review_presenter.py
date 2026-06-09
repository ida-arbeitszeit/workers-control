from __future__ import annotations

from dataclasses import dataclass
from typing import List

from workers_control.core.interactors.list_plans_with_pending_review import (
    ListPlansWithPendingReviewInteractor as Interactor,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class ListPlansWithPendingReviewPresenter:
    @dataclass
    class Plan:
        product_name: str
        planner_name: str
        plan_details_url: str
        company_summary_url: str
        review_plan_url: str

    @dataclass
    class ViewModel:
        show_plan_list: bool
        plans: List[ListPlansWithPendingReviewPresenter.Plan]

    url_index: UrlIndex
    translator: Translator

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(text=self.translator.gettext("List unreviewed plans"), url=None)
        ]

    def list_plans_with_pending_review(
        self, response: Interactor.Response
    ) -> ViewModel:
        return self.ViewModel(
            show_plan_list=bool(response.plans),
            plans=[
                self.Plan(
                    product_name=plan.product_name,
                    planner_name=plan.planner_name,
                    plan_details_url=self.url_index.get_plan_details_url(
                        plan_id=plan.id
                    ),
                    company_summary_url=self.url_index.get_company_summary_url(
                        company_id=plan.planner_id
                    ),
                    review_plan_url=self.url_index.get_plan_review_url(plan.id),
                )
                for plan in response.plans
            ],
        )
