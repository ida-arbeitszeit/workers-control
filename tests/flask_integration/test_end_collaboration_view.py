from uuid import uuid4

from .base_test_case import ViewTestCase

URL = "/company/end_collaboration"


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_404_is_returned_when_no_form_data_is_sent(
        self,
    ) -> None:
        data: dict = {}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_404_is_returned_when_plan_does_not_exist(
        self,
    ) -> None:
        collaboration = self.collaboration_generator.create_collaboration()
        data = {"plan_id": str(uuid4()), "collaboration_id": str(collaboration)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_404_is_returned_when_collab_does_not_exist(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        data = {"plan_id": str(plan), "collaboration_id": str(uuid4())}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_404_is_returned_when_collab_and_plan_do_exist_but_requester_is_neither_planner_nor_coordinator(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(plans=[plan])
        data = {"plan_id": str(plan), "collaboration_id": str(collaboration)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_302_is_returned_when_collab_and_plan_do_exist_and_requester_is_planner(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.company)
        collaboration = self.collaboration_generator.create_collaboration(plans=[plan])
        data = {"plan_id": str(plan), "collaboration_id": str(collaboration)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 302

    def test_302_is_returned_when_collab_and_plan_do_exist_and_requester_is_coordinator(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(
            plans=[plan], coordinator=self.company
        )
        data = {"plan_id": str(plan), "collaboration_id": str(collaboration)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 302
