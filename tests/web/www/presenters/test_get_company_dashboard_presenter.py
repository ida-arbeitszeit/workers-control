from typing import Optional
from uuid import uuid4

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.get_company_dashboard import (
    GetCompanyDashboardInteractor as Interactor,
)
from workers_control.web.www.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)


class CompanyDashboardBaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCompanyDashboardPresenter)

    def get_interactor_response(
        self,
        has_workers: bool = False,
        company_info: Optional[Interactor.Response.CompanyInfo] = None,
    ) -> Interactor.Response:
        if company_info is None:
            company_info = Interactor.Response.CompanyInfo(
                id=uuid4(), name="company name", email="mail@test.de"
            )
        return Interactor.Response(
            company_info=company_info,
            has_workers=has_workers,
        )


class CompanyDashboardPresenterTests(CompanyDashboardBaseTestCase):
    def test_presenter_successfully_presents_a_interactor_response(self):
        self.assertTrue(self.presenter.present(self.get_interactor_response()))

    def test_presenter_correctly_shows_that_company_has_no_workers(self):
        has_workers = self.presenter.present(
            self.get_interactor_response(has_workers=False)
        ).has_workers
        self.assertFalse(has_workers)

    def test_presenter_correctly_shows_company_name(self):
        view_model = self.presenter.present(
            self.get_interactor_response(
                company_info=Interactor.Response.CompanyInfo(
                    id=uuid4(), name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_name, "company test name")

    def test_presenter_correctly_shows_company_id(self):
        company_id = uuid4()
        view_model = self.presenter.present(
            self.get_interactor_response(
                company_info=Interactor.Response.CompanyInfo(
                    id=company_id, name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_id, str(company_id))

    def test_presenter_correctly_shows_company_email(self):
        view_model = self.presenter.present(
            self.get_interactor_response(
                company_info=Interactor.Response.CompanyInfo(
                    id=uuid4(), name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_email, "mail@test.de")


class CompanyDashboardTileTests(CompanyDashboardBaseTestCase):
    def test_accounts_tile_has_correct_title(self) -> None:
        view_model = self.presenter.present(self.get_interactor_response())
        self.assertEqual(
            view_model.accounts_tile.title, self.translator.gettext("Accounts")
        )

    def test_accounts_tile_has_correct_subtitle(self) -> None:
        view_model = self.presenter.present(self.get_interactor_response())
        self.assertEqual(
            view_model.accounts_tile.subtitle,
            self.translator.gettext("You have four accounts"),
        )

    def test_accounts_tile_has_correct_icon(self) -> None:
        view_model = self.presenter.present(self.get_interactor_response())
        self.assertEqual(view_model.accounts_tile.icon, "chart-line")

    def test_accounts_tile_has_url_that_leads_to_accounts_of_company_from_interactor_response(
        self,
    ) -> None:
        expected_company_id = uuid4()
        view_model = self.presenter.present(
            self.get_interactor_response(
                company_info=Interactor.Response.CompanyInfo(
                    id=expected_company_id,
                    name="company test name",
                    email="mail@test.de",
                )
            )
        )
        self.assertEqual(
            view_model.accounts_tile.url,
            self.url_index.get_company_accounts_url(company_id=expected_company_id),
        )
