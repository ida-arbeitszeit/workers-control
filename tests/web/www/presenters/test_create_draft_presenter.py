from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.create_plan_draft import RejectionReason, Response
from workers_control.web.www.presenters.create_draft_presenter import (
    CreateDraftPresenter,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateDraftPresenter)

    def test_on_successful_draft_creation_redirect_to_my_drafts_page(self) -> None:
        draft_id = uuid4()
        response = Response(draft_id=draft_id, rejection_reason=None)
        view_model = self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.url_index.get_my_plan_drafts_url(), view_model.redirect_url
        )

    def test_on_failed_plan_creation_dont_redirect(self) -> None:
        response = Response(
            draft_id=None,
            rejection_reason=RejectionReason.planner_does_not_exist,
        )
        view_model = self.presenter.present_plan_creation(response)
        self.assertIsNone(view_model.redirect_url)

    def test_on_successful_creation_show_message(self) -> None:
        draft_id = uuid4()
        response = Response(draft_id=draft_id, rejection_reason=None)
        self.presenter.present_plan_creation(response)
        self.assertTrue(self.notifier.infos)

    def test_on_successful_creation_show_proper_message_text(self) -> None:
        draft_id = uuid4()
        response = Response(draft_id=draft_id, rejection_reason=None)
        self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.notifier.infos[0],
            self.translator.gettext("Plan draft successfully created"),
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateDraftPresenter)

    def test_two_navbar_items_are_shown(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(len(navbar_items), 2)

    def test_first_navbar_item_has_text_my_plans(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(navbar_items[0].text, self.translator.gettext("My plans"))

    def test_first_navbar_item_links_to_my_plans(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(navbar_items[0].url, self.url_index.get_my_plans_url())

    def test_second_navbar_item_has_text_create_plan(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(navbar_items[1].text, self.translator.gettext("Create plan"))

    def test_second_navbar_item_has_no_link(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertIsNone(navbar_items[1].url)
