from dataclasses import replace
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.get_coop_summary import (
    AssociatedPlan,
    GetCoopSummaryResponse,
)
from workers_control.web.www.presenters.get_collab_summary_presenter import (
    GetCollabSummarySuccessPresenter,
)


class GetCollabSummarySuccessPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCollabSummarySuccessPresenter)
        self.session.login_company(company=uuid4())

    def test_collab_id_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(view_model.collab_id, str(view_model.collab_id))

    def test_collab_name_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(view_model.collab_name, view_model.collab_name)

    @parameterized.expand(["collab def\ncollab def2", "collab def\n\rcollab def2"])
    def test_collab_definition_is_displayed_correctly_as_list_of_strings(
        self, collab_definition: str
    ) -> None:
        expected_definition = collab_definition.splitlines()
        collab_summary = self.get_collab_summary(collab_definition=collab_definition)
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(view_model.collab_definition, expected_definition)

    def test_no_url_to_request_coordination_transfer_page_is_displayed_if_user_is_not_coordinator(
        self,
    ) -> None:
        collab_summary = self.get_collab_summary(requester_is_coordinator=False)
        view_model = self.presenter.present(collab_summary)
        self.assertIsNone(view_model.transfer_coordination_url)

    def test_url_to_request_coordination_transfer_page_is_displayed_if_user_is_coordinator(
        self,
    ) -> None:
        collab_summary = self.get_collab_summary(requester_is_coordinator=True)
        view_model = self.presenter.present(collab_summary)
        self.assertIsNotNone(view_model.transfer_coordination_url)

    def test_correct_url_to_request_coordination_transfer_page_is_displayed_if_user_is_coordinator(
        self,
    ) -> None:
        collab_summary = self.get_collab_summary(requester_is_coordinator=True)
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.transfer_coordination_url,
            self.url_index.get_request_coordination_transfer_url(
                collab_id=collab_summary.coop_id,
            ),
        )

    def test_coordinator_id_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.current_coordinator_id,
            str(collab_summary.current_coordinator),
        )

    def test_coordinator_name_is_displayed_correctly(self) -> None:
        expected_coordinator_name = "A coordinator name"
        collab_summary = self.get_collab_summary(
            coordinator_name=expected_coordinator_name
        )
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.current_coordinator_name,
            expected_coordinator_name,
        )

    def test_link_to_coordinators_company_summary_page_is_displayed_correctly(
        self,
    ) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.current_coordinator_url,
            self.url_index.get_company_summary_url(
                company_id=collab_summary.current_coordinator,
            ),
        )

    def test_link_to_list_of_coordinators_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.list_of_coordinators_url,
            self.url_index.get_list_of_coordinators_url(
                collaboration_id=collab_summary.coop_id,
            ),
        )

    def test_collab_price_is_displayed_correctly_if_it_is_not_none(self) -> None:
        collab_price = Decimal(50.005)
        expected_collab_price = f"{round(collab_price, 2)}"
        collab_summary = self.get_collab_summary(collab_price=collab_price)
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.collab_price,
            expected_collab_price,
        )

    def test_collab_price_is_displayed_as_a_dash_if_collab_price_is_none(self) -> None:
        collab_summary = self.get_collab_summary()
        collab_summary = replace(collab_summary, coop_price=None)
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.collab_price,
            "-",
        )

    def test_first_plans_name_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.plans[0].plan_name, collab_summary.plans[0].plan_name
        )

    @parameterized.expand([(Decimal("1"),), (Decimal("0"),), (Decimal("0.509"),)])
    def test_first_plans_individual_price_is_displayed_correctly(
        self, plan_individual_price: Decimal
    ) -> None:
        expected_price = f"{round(plan_individual_price, 2)}"
        collab_summary = self.get_collab_summary(
            plans=[
                self.get_associated_plan(plan_individual_price=plan_individual_price)
            ]
        )
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(view_model.plans[0].plan_individual_price, expected_price)

    def test_first_plans_plan_id_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        assert view_model.plans[0].plan_id == str(collab_summary.plans[0].plan_id)

    def test_first_plans_planner_name_is_displayed_correctly(self) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.plans[0].planner_name,
            collab_summary.plans[0].planner_name,
        )

    def test_url_to_first_plans_planner_company_summary_page_is_displayed_correctly(
        self,
    ) -> None:
        collab_summary = self.get_collab_summary()
        view_model = self.presenter.present(collab_summary)
        self.assertEqual(
            view_model.plans[0].planner_url,
            self.url_index.get_company_summary_url(
                company_id=collab_summary.plans[0].planner_id,
            ),
        )

    def test_no_plans_are_shown_when_there_are_no_plans_associated(self) -> None:
        collab_summary = self.get_collab_summary(plans=[])
        view_model = self.presenter.present(collab_summary)
        assert not view_model.plans

    def test_two_plans_are_shown_when_there_are_two_plans_associated(self) -> None:
        collab_summary = self.get_collab_summary(
            plans=[self.get_associated_plan(), self.get_associated_plan()]
        )
        view_model = self.presenter.present(collab_summary)
        assert len(view_model.plans) == 2

    @parameterized.expand(
        [
            (True, True, True),
            (True, False, True),
            (False, True, True),
            (False, False, False),
        ]
    )
    def test_end_collab_button_of_plan_is_shown_only_when_requester_is_coordinator_or_planner(
        self,
        requester_is_coordinator: bool,
        requester_is_planner: bool,
        button_is_shown: bool,
    ) -> None:
        plan = self.get_associated_plan(requester_is_planner=requester_is_planner)
        collab_summary = self.get_collab_summary(
            requester_is_coordinator=requester_is_coordinator, plans=[plan]
        )
        view_model = self.presenter.present(response=collab_summary)
        assert view_model.plans[0].show_end_collab_button == button_is_shown

    def get_associated_plan(
        self,
        requester_is_planner: Optional[bool] = None,
        plan_individual_price: Optional[Decimal] = None,
    ) -> AssociatedPlan:
        if requester_is_planner is None:
            requester_is_planner = False
        if plan_individual_price is None:
            plan_individual_price = Decimal("1")
        return AssociatedPlan(
            plan_id=uuid4(),
            plan_name="plan_name",
            plan_individual_price=plan_individual_price,
            planner_id=uuid4(),
            planner_name="A Collaborating Company Collab.",
            requester_is_planner=requester_is_planner,
        )

    def get_collab_summary(
        self,
        plans: Optional[list[AssociatedPlan]] = None,
        requester_is_coordinator: Optional[bool] = None,
        collab_definition: Optional[str] = None,
        coordinator_name: Optional[str] = None,
        collab_price: Optional[Decimal] = None,
    ) -> GetCoopSummaryResponse:
        if plans is None:
            plans = [self.get_associated_plan()]
        if requester_is_coordinator is None:
            requester_is_coordinator = True
        if collab_definition is None:
            collab_definition = "collab def\ncollab def2"
        if coordinator_name is None:
            coordinator_name = "coordinator name"
        if collab_price is None:
            collab_price = Decimal(50.005)
        return GetCoopSummaryResponse(
            requester_is_coordinator=requester_is_coordinator,
            coop_id=uuid4(),
            coop_name="collab name",
            coop_definition=collab_definition,
            current_coordinator=uuid4(),
            current_coordinator_name=coordinator_name,
            coop_price=collab_price,
            plans=plans,
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCollabSummarySuccessPresenter)

    def test_navbar_shows_collaboration_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].text, self.translator.gettext("Collaboration"))
        self.assertIsNone(items[0].url)
