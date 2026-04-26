from typing import Optional

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionResponse,
)
from workers_control.web.www.presenters.register_productive_consumption_presenter import (
    RegisterProductiveConsumptionPresenter,
)

reasons = RegisterProductiveConsumptionResponse.RejectionReason


class RegisterProductiveConsumptionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterProductiveConsumptionPresenter)

    def test_show_confirmation_when_registration_was_successful(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=None,
            )
        )
        self.assertIn(
            self.translator.gettext("Successfully registered."), self.notifier.infos
        )

    def test_missing_plan_show_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.plan_not_found,
            )
        )
        self.assertIn(
            self.translator.gettext("Plan does not exist."), self.notifier.warnings
        )

    def test_invalid_consumption_type_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.invalid_consumption_type,
            )
        )
        self.assertIn(
            self.translator.gettext("The specified type of consumption is invalid."),
            self.notifier.warnings,
        )

    def test_inactive_plan_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.plan_is_not_active,
            )
        )
        self.assertIn(
            self.translator.gettext(
                "The specified plan has expired. Please contact the provider to obtain a current plan ID."
            ),
            self.notifier.warnings,
        )

    def test_trying_to_consume_public_service_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.cannot_consume_public_service,
            )
        )
        self.assertIn(
            self.translator.gettext(
                "Registration failed. Companies cannot acquire public products."
            ),
            self.notifier.warnings,
        )

    def test_trying_to_consume_own_product_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.consumer_is_planner,
            )
        )
        self.assertIn(
            self.translator.gettext(
                "Registration failed. Companies cannot acquire their own products."
            ),
            self.notifier.warnings,
        )

    def test_that_redirect_url_is_not_set_when_registration_got_rejected(self) -> None:
        response = self.create_failed_response()
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.redirect_url)

    def test_that_redirect_url_is_set_when_response_is_success(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present(response)
        self.assertIsNotNone(view_model.redirect_url)

    def test_that_user_gets_redirected_to_company_consumptions(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_company_consumptions_url(),
        )

    def create_success_response(self) -> RegisterProductiveConsumptionResponse:
        return RegisterProductiveConsumptionResponse(rejection_reason=None)

    def create_failed_response(
        self,
        reason: Optional[RegisterProductiveConsumptionResponse.RejectionReason] = None,
    ) -> RegisterProductiveConsumptionResponse:
        if reason is None:
            reason = reasons.consumer_is_planner
        return RegisterProductiveConsumptionResponse(rejection_reason=reason)


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterProductiveConsumptionPresenter)

    def test_two_navbar_items_are_shown(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(len(navbar_items), 2)

    def test_first_navbar_item_has_text_offers(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(navbar_items[0].text, self.translator.gettext("Offers"))

    def test_first_navbar_item_links_to_query_offers(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(navbar_items[0].url, self.url_index.get_query_offers_url())

    def test_second_navbar_item_has_text_register_productive_consumption(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertEqual(
            navbar_items[1].text,
            self.translator.gettext("Registration of productive consumption"),
        )

    def test_second_navbar_item_has_no_link(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        self.assertIsNone(navbar_items[1].url)
