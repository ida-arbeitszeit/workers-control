from typing import Optional
from uuid import UUID, uuid4

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_min_utc
from workers_control.core.interactors.list_coordinations_of_company import (
    CollaborationInfo,
    ListCoordinationsOfCompanyResponse,
)
from workers_control.core.interactors.list_my_collaborating_plans import (
    ListMyCollaboratingPlansInteractor,
)
from workers_control.core.interactors.show_company_collaborations import (
    InboundCollabRequest,
    OutboundCollabRequest,
    Response,
)
from workers_control.web.www.presenters.show_my_collaborations_presenter import (
    ShowMyCollaborationsPresenter,
)

LIST_COORDINATIONS_RESPONSE_LEN_1 = ListCoordinationsOfCompanyResponse(
    coordinations=[
        CollaborationInfo(
            id=uuid4(),
            creation_date=datetime_min_utc(),
            name="collab name",
            definition="first paragraph\nsecond paragraph",
            count_plans_in_collab=3,
        )
    ]
)


def get_collab_plans_response_length_1(
    plan_id: Optional[UUID] = None, collab_id: Optional[UUID] = None
) -> ListMyCollaboratingPlansInteractor.Response:
    if plan_id is None:
        plan_id = uuid4()
    if collab_id is None:
        collab_id = uuid4()
    return ListMyCollaboratingPlansInteractor.Response(
        collaborating_plans=[
            ListMyCollaboratingPlansInteractor.CollaboratingPlan(
                plan_id=plan_id,
                plan_name="test plan name",
                collab_id=collab_id,
                collab_name="test collab name",
            )
        ]
    )


class ShowMyCollaborationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCollaborationsPresenter)

    def test_coordinations_are_presented_correctly(self) -> None:
        presentation = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            show_company_collaborations_response=Response(
                inbound_collaboration_requests=[
                    InboundCollabRequest(
                        collab_id=uuid4(),
                        collab_name="collab name",
                        plan_id=uuid4(),
                        plan_name="plan name",
                        planner_name="planner name",
                        planner_id=uuid4(),
                    )
                ],
                outbound_collaboration_requests=[
                    OutboundCollabRequest(
                        plan_id=uuid4(),
                        plan_name="plan name",
                        collab_id=uuid4(),
                        collab_name="collab name",
                    )
                ],
            ),
            list_my_collaborating_plans_response=get_collab_plans_response_length_1(),
        )
        self.assertEqual(len(presentation.list_of_coordinations.rows), 1)
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].collab_id,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id),
        )
        collab_id = LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].collab_summary_url,
            self.url_index.get_collab_summary_url(collab_id=collab_id),
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].collab_creation_date,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].creation_date),
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].collab_name,
            LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].name,
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].collab_definition,
            ["first paragraph", "second paragraph"],
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].count_plans_in_collab,
            str(
                LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].count_plans_in_collab
            ),
        )


class InboundTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCollaborationsPresenter)
        self.COLLAB_ID = uuid4()
        self.PLAN_ID = uuid4()
        self.PLANNER_ID = uuid4()
        self.view_model = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            show_company_collaborations_response=Response(
                inbound_collaboration_requests=[
                    InboundCollabRequest(
                        collab_id=self.COLLAB_ID,
                        collab_name="collab name",
                        plan_id=self.PLAN_ID,
                        plan_name="plan name",
                        planner_name="planner name",
                        planner_id=self.PLANNER_ID,
                    )
                ],
                outbound_collaboration_requests=[],
            ),
            list_my_collaborating_plans_response=get_collab_plans_response_length_1(),
        )

    def test_inbound_collab_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_inbound_collab_requests.rows[0].collab_name,
        )

    def test_inbound_plan_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_inbound_collab_requests.rows[0].plan_name,
        )

    def test_inbound_planner_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_inbound_collab_requests.rows[0].planner_name,
        )

    def test_inbound_collab_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_collab_requests.rows[0].collab_id,
            str(self.COLLAB_ID),
        )

    def test_inbound_plan_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_collab_requests.rows[0].plan_id,
            str(self.PLAN_ID),
        )

    def test_inbound_plan_url_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_collab_requests.rows[0].plan_url,
            self.url_index.get_plan_details_url(plan_id=self.PLAN_ID),
        )

    def test_inbound_planner_url_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_collab_requests.rows[0].planner_url,
            self.url_index.get_company_summary_url(company_id=self.PLANNER_ID),
        )


class OutboundTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCollaborationsPresenter)
        self.COLLAB_ID = uuid4()
        self.PLAN_ID = uuid4()
        self.view_model = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            show_company_collaborations_response=Response(
                outbound_collaboration_requests=[
                    OutboundCollabRequest(
                        plan_id=self.PLAN_ID,
                        plan_name="plan name",
                        collab_id=self.COLLAB_ID,
                        collab_name="collab name",
                    )
                ],
                inbound_collaboration_requests=[],
            ),
            list_my_collaborating_plans_response=get_collab_plans_response_length_1(),
        )

    def test_outbound_plan_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_outbound_collab_requests.rows[0].plan_id,
            str(self.PLAN_ID),
        )

    def test_outbound_collab_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_outbound_collab_requests.rows[0].collab_id,
            str(self.COLLAB_ID),
        )

    def test_outbound_collab_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_outbound_collab_requests.rows[0].collab_name,
        )

    def test_outbound_plan_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_outbound_collab_requests.rows[0].plan_name,
        )

    def test_outbound_plan_url_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_outbound_collab_requests.rows[0].plan_url,
            self.url_index.get_plan_details_url(plan_id=self.PLAN_ID),
        )


class CollaboratingPlansTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCollaborationsPresenter)
        self.COLLAB_ID = uuid4()
        self.PLAN_ID = uuid4()
        self.view_model = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            show_company_collaborations_response=Response(
                outbound_collaboration_requests=[],
                inbound_collaboration_requests=[],
            ),
            list_my_collaborating_plans_response=get_collab_plans_response_length_1(
                plan_id=self.PLAN_ID, collab_id=self.COLLAB_ID
            ),
        )

    def test_show_one_plan_if_one_plan_exists(self) -> None:
        assert len(self.view_model.list_of_my_collaborating_plans.rows) == 1

    def test_plan_id_is_shown_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_my_collaborating_plans.rows[0].plan_id,
            str(self.PLAN_ID),
        )

    def test_collab_id_is_shown_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_my_collaborating_plans.rows[0].collab_id,
            str(self.COLLAB_ID),
        )

    def test_name_of_plan_is_shown(self) -> None:
        assert self.view_model.list_of_my_collaborating_plans.rows[0].plan_name

    def test_name_of_collaboration_is_shown(self) -> None:
        assert self.view_model.list_of_my_collaborating_plans.rows[0].collab_name

    def test_plan_url_is_shown_correctly(self) -> None:
        self.assertEqual(
            self.url_index.get_plan_details_url(plan_id=self.PLAN_ID),
            self.view_model.list_of_my_collaborating_plans.rows[0].plan_url,
        )

    def test_collab_url_is_shown_correctly(self) -> None:
        self.assertEqual(
            self.url_index.get_collab_summary_url(collab_id=self.COLLAB_ID),
            self.view_model.list_of_my_collaborating_plans.rows[0].collab_url,
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCollaborationsPresenter)

    def test_navbar_shows_my_collaborations_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].text, self.translator.gettext("My collaborations"))
        self.assertIsNone(items[0].url)
