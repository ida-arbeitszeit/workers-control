from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.register_hours_worked import (
    RegisterHoursWorkedResponse,
)
from workers_control.web.www.controllers.register_hours_worked_controller import (
    ControllerRejection,
)
from workers_control.web.www.presenters.register_hours_worked_presenter import (
    RegisterHoursWorkedPresenter,
)

SUCCESS_INTERACTOR_RESPONSE = RegisterHoursWorkedResponse(
    rejection_reason=None, registered_hours_worked_id=uuid4()
)

REJECTED_INTERACTOR_RESPONSE = RegisterHoursWorkedResponse(
    rejection_reason=RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company,
    registered_hours_worked_id=None,
)

REJECTED_CONTROLLER_RES_INVALID_INPUT = ControllerRejection(
    reason=ControllerRejection.RejectionReason.invalid_input
)

REJECTED_CONTROLLER_RES_NEGATIVE_AMOUNT = ControllerRejection(
    reason=ControllerRejection.RejectionReason.negative_amount
)


class PresentInteractorResponseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterHoursWorkedPresenter)

    def test_presenter_renders_warning_if_interactor_response_is_rejected(self):
        self.presenter.present_interactor_response(REJECTED_INTERACTOR_RESPONSE)
        self.assertTrue(self.notifier.warnings)
        self.assertFalse(self.notifier.infos)

    def test_presenter_returns_status_404_if_interactor_response_is_rejected(self):
        view_model = self.presenter.present_interactor_response(
            REJECTED_INTERACTOR_RESPONSE
        )
        self.assertEqual(view_model.status_code, 404)

    def test_presenter_does_not_redirect_when_interactor_response_is_rejected(self):
        view_model = self.presenter.present_interactor_response(
            REJECTED_INTERACTOR_RESPONSE
        )
        self.assertIsNone(view_model.redirect_url)

    def test_presenter_renders_info_if_interactor_response_is_successfull(self):
        self.presenter.present_interactor_response(SUCCESS_INTERACTOR_RESPONSE)
        self.assertTrue(self.notifier.infos)
        self.assertFalse(self.notifier.warnings)

    def test_presenter_returns_status_302_if_interactor_response_is_successfull(self):
        view_model = self.presenter.present_interactor_response(
            SUCCESS_INTERACTOR_RESPONSE
        )
        self.assertEqual(view_model.status_code, 302)

    def test_presenter_redirects_to_registered_hours_worked_view_on_success(self):
        view_model = self.presenter.present_interactor_response(
            SUCCESS_INTERACTOR_RESPONSE
        )
        self.assertEqual(
            view_model.redirect_url, self.url_index.get_registered_hours_worked_url()
        )

    def test_that_the_user_is_notified_about_success(self) -> None:
        self.presenter.present_interactor_response(SUCCESS_INTERACTOR_RESPONSE)
        assert (
            self.translator.gettext("Labour hours successfully registered")
            in self.notifier.infos
        )


class PresentControllerResponseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterHoursWorkedPresenter)

    def test_presenter_renders_correct_warning_if_controller_rejects_invalid_input(
        self,
    ):
        self.presenter.present_controller_warnings(
            REJECTED_CONTROLLER_RES_INVALID_INPUT
        )
        self.assertTrue(self.notifier.warnings)
        self.assertFalse(self.notifier.infos)
        self.assertIn(self.translator.gettext("Invalid input"), self.notifier.warnings)

    def test_presenter_renders_correct_warning_if_controller_rejects_negative_amount(
        self,
    ):
        self.presenter.present_controller_warnings(
            REJECTED_CONTROLLER_RES_NEGATIVE_AMOUNT
        )
        self.assertTrue(self.notifier.warnings)
        self.assertFalse(self.notifier.infos)
        self.assertIn(
            self.translator.gettext("A negative amount is not allowed."),
            self.notifier.warnings,
        )


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterHoursWorkedPresenter)

    def test_two_navbar_items_are_shown(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(len(navbar_items), 2)

    def test_first_navbar_item_has_text_registered_working_hours(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(
            navbar_items[0].text, self.translator.gettext("Registered working hours")
        )

    def test_first_navbar_item_links_to_registered_hours_worked(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(
            navbar_items[0].url, self.url_index.get_registered_hours_worked_url()
        )

    def test_second_navbar_item_has_text_register_hours_worked(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(
            navbar_items[1].text, self.translator.gettext("Register hours worked")
        )

    def test_second_navbar_item_has_no_link(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertIsNone(navbar_items[1].url)
