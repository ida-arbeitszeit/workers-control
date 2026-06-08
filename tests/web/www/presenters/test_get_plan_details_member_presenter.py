from tests.web.base_test_case import BaseTestCase
from workers_control.web.www.presenters.get_plan_details_member_presenter import (
    GetPlanDetailsMemberMemberPresenter,
)


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanDetailsMemberMemberPresenter)

    def test_navbar_shows_plan_information_as_current_page(self) -> None:
        items = self.presenter.create_navbar_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].text, self.translator.gettext("Plan information"))
        self.assertIsNone(items[0].url)
