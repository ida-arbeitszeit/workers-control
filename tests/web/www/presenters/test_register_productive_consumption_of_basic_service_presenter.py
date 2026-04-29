from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.register_productive_consumption_of_basic_service import (
    RejectionReason,
    Response,
)
from workers_control.web.www.presenters.register_productive_consumption_of_basic_service_presenter import (
    Redirect,
    RegisterProductiveConsumptionOfBasicServicePresenter,
    RenderForm,
)


class RegisterProductiveConsumptionOfBasicServicePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(
            RegisterProductiveConsumptionOfBasicServicePresenter
        )

    def test_success_displays_info_notification(self) -> None:
        self.presenter.present(
            Response(rejection_reason=None),
            request=FakeRequest(),
        )
        self.assertIn(
            self.translator.gettext("Successfully registered."),
            self.notifier.infos,
        )

    def test_success_returns_redirect(self) -> None:
        view_model = self.presenter.present(
            Response(rejection_reason=None),
            request=FakeRequest(),
        )
        assert isinstance(view_model, Redirect)

    def test_success_redirects_to_company_consumptions_url(self) -> None:
        view_model = self.presenter.present(
            Response(rejection_reason=None),
            request=FakeRequest(),
        )
        assert isinstance(view_model, Redirect)
        assert view_model.url == self.url_index.get_company_consumptions_url()

    @parameterized.expand([(reason,) for reason in RejectionReason])
    def test_rejection_results_in_render_form(self, reason: RejectionReason) -> None:
        view_model = self.presenter.present(
            Response(rejection_reason=reason),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)

    def test_basic_service_not_found_message(self) -> None:
        view_model = self.presenter.present(
            Response(rejection_reason=RejectionReason.basic_service_not_found),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        assert (
            self.translator.gettext(
                "There is no basic service with the specified ID in the database."
            )
            in view_model.form.basic_service_id_errors
        )

    def test_basic_service_not_found_returns_404(self) -> None:
        view_model = self.presenter.present(
            Response(rejection_reason=RejectionReason.basic_service_not_found),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        assert view_model.status_code == 404


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(
            RegisterProductiveConsumptionOfBasicServicePresenter
        )

    def test_two_navbar_items_are_shown(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        assert len(navbar_items) == 2

    def test_first_navbar_item_has_text_offers(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        assert navbar_items[0].text == self.translator.gettext("Offers")

    def test_first_navbar_item_links_to_query_offers(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        assert navbar_items[0].url == self.url_index.get_query_offers_url()

    def test_second_navbar_item_has_text_register_productive_consumption(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        assert navbar_items[1].text == self.translator.gettext(
            "Registration of productive consumption"
        )

    def test_second_navbar_item_has_no_link(self) -> None:
        navbar_items = self.presenter.create_navbar_items()
        assert navbar_items[1].url is None
